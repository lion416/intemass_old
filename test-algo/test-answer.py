#! /usr/bin/python
#
# answer.py: Defines class for representing student responses (Answer).
#

# Local packages
#
from common import *
debug_print("algo/answer.py: " + debug_timestamp())
import wordnet
import text

# Other packages
#
import re
import nltk
import math
from django.conf import settings
import logging

#------------------------------------------------------------------------
# Utility functions

# find_most_freq_term(terms, freq_dist): Returns entry in TERMS with highest
# frequency in FREQ_DIST (hash), ignoring terms with zero frequency.
# Note: Some of the terms might not occur in the hash.
# EX: find_most_freq_term(['dawg', 'mouse'], {'dog':9, 'cat':7, 'mouse':11}) => 'mouse'
# EX: find_most_freq_term(['kat', 'moose'], {'dog':9, 'cat':7, 'mouse':11}) => ''
#
def find_most_freq_term(terms, freq_dist_hash):
    max_freq = 0
    max_word = None
    for word in terms:
        if (freq_dist_hash.has_key(word) and (freq_dist_hash[word] > max_freq)):
            max_freq = freq_dist_hash[word]
            max_word = word
    debug_print("find_most_freq_term%s => %s" % (str((terms, freq_dist_hash)), max_word), level=6)
    return max_word

# list_difference(list1, list2): Returns items in LIST1 not in LIST2.
# EX: list_difference([3, 2, 1], [1, 2]) => [3]
#
def list_difference(list1, list2):
    diff_list = [item for item in set(list1).difference(list2)]
    debug_print("list_difference%s => %s" % (str((list1, list2)), str(diff_list)), level=5)
    return (diff_list)

#------------------------------------------------------------------------

# Answer: Class for representing student (textual) answer

class Answer:
    # Answer(): initialize thresholds and other settings
    # EX: ans = Answer(); (ans.dist_threshold > 0.20) => True
    #
    def __init__(self):
        debug_print("Answer()", level=6)
        # Matching thresholds
        self.dist_threshold = 0.25
        self.multisen_matchrate = 0.3
        self.sen_threshold = 0.33
        self.multisen_threshold = 0.4
        self.logger = logging.getLogger(__name__)
        # Settings for extensions
        # Note: These might not be in the settings file, so accessed indirectly (e.g., via hasattr/getattr).
        self.apply_synonym_expansion = get_property_value(settings, 'APPLY_SYNONYM_EXPANSION', False)
        self.apply_ancestor_expansion = get_property_value(settings, 'APPLY_ANCESTOR_EXPANSION', False)
        self.max_ancestor_links = get_property_value(settings, 'MAX_ANCESTOR_LINKS', 5)
        self.use_part_of_speech = get_property_value(settings, 'USE_PART_OF_SPEECH', False)
        self.only_match_sentence_once = get_property_value(settings, 'ONLY_MATCH_SENTENCE_ONCE', False)
        self.synonym_scale_factor = get_property_value(settings, 'SYNONYM_SCALE_FACTOR', 0.90)
        self.ancestor_scale_factor = get_property_value(settings, 'ANCESTOR_SCALE_FACTOR', 0.45)
        self.use_true_tf_idf = get_property_value(settings, 'USE_TRUE_TF_IDF', False)
        # Check environment for overrides to extension settings when debugging
        if __debug__: 
            self.apply_synonym_expansion = getenv_boolean("APPLY_SYNONYM_EXPANSION", self.apply_synonym_expansion)
            self.apply_ancestor_expansion = getenv_boolean("APPLY_ANCESTOR_EXPANSION", self.apply_ancestor_expansion)
            self.max_ancestor_links = getenv_number("MAX_ANCESTOR_LINKS", self.max_ancestor_links)
            self.use_part_of_speech = getenv_boolean("USE_PART_OF_SPEECH", self.use_part_of_speech)
            self.only_match_sentence_once = getenv_boolean("ONLY_MATCH_SENTENCE_ONCE", self.only_match_sentence_once)
            self.synonym_scale_factor = getenv_number("SYNONYM_SCALE_FACTOR", self.synonym_scale_factor)
            self.ancestor_scale_factor = getenv_number("ANCESTOR_SCALE_FACTOR", self.ancestor_scale_factor)
            self.use_true_tf_idf = getenv_boolean("USE_TRUE_TF_IDF", self.use_true_tf_idf)
        # Other settings
        nltk.data.path = [settings.NLTKDATAPATH]


    # SentenceAnalysis(full_text, text_freq_dist): Split FULL_TEXT info sentences and derive term
    # vectors computed using TF/IDF-style weighting, accounting for frequencies in TEXT_FREQ_DIST.
    # Note: Changes made here should be synchronized with SentenceCal in standard.py.
    # TODO: Use common auxiliary function for vector computation.
    # TODO: See why stop words are not removed here as in CalVector from standard.py.
    #
    # EX: ans.SentenceAnalysis("The lawyer chased the vehicle.\n  The vehicle chased back.", <FreqDist: 'chased': 2, 'vehicle': 2, 'lawyer': 1>) => [{'StuS': 'The lawyer chased the vehicle.', 'No': 1, 'StuSVec': {'chased': 1.1736001944781467, 'lawyer': 2.3472003889562933, 'vehicle': 1.1736001944781467}, 'StuWords': ['lawyer', 'chased', 'vehicle']}, {'StuS': 'The vehicle chased back.', 'No': 2, 'StuSVec': {'chased': 1.1736001944781467, 'lawyer': 0, 'vehicle': 1.1736001944781467}, 'StuWords': ['vehicle', 'chased', 'back']}]
    #
    def SentenceAnalysis(self, fulltext, textfdist):
        ans_sentencelist = []
        text = fulltext.replace('\n', ' ')

        # Separate text into sentences
        # TODO: See if NLTK sentence tokenizer works better
        #p = re.compile(r'.+\.')
        p = re.compile(r'([\w\"\'\<\(][\S ]+?[\.!?])[ \n\"]')
        keysen = p.findall(text)
        sen_no = 0
        for sen in keysen:
            debug_print("sen: " + str(sen), level=6)
            sen_no += 1
            # Tokenize text, part-of-speech tag, derive WordNet base word (lemma), and then add information for words found.
            # Note: An optional part-of-speech tag prefix can be included.
            # TODO: Isolate text preprocessing code in a separate function 
            text = nltk.word_tokenize(sen)
            part_of_speech_tagged_words =  nltk.pos_tag(text)
            text_words = list(nltk.corpus.wordnet.morphy(word.lower()) for (word, tag) in part_of_speech_tagged_words)
            text_words_proper = list(word for word in text_words if word)
            if self.use_part_of_speech:
                # Prefix each word with wordnet part-of-speech indicator (e.g., ['fast', 'car'] => ['a:fast', 'n:car'])
                text_words_proper = [wordnet.get_part_of_speech(tag) + ":" + word
                                     for (word, (token, tag)) in zip(text_words, part_of_speech_tagged_words) 
                                     if word]
            ans_sentencelist.append({'StuS': sen,
                                     'StuWords': text_words_proper,
                                     'No': sen_no})

        # Compute TF/IDF-style weighting scheme
        for sentence in ans_sentencelist:
            debug_print("sentence: " + str(sentence), level=6)
            fdist = nltk.FreqDist(sentence['StuWords'])
            max_freq = max([f for f in fdist.values()])
            log_max_freq = math.log(max_freq) if (max_freq > 1) else 1
            senvec = {}
            for word in sorted(textfdist):
                if fdist[word]:
                    wordfreq = sum(1 for senten in ans_sentencelist if word in senten['StuWords'])
                    if (self.use_true_tf_idf):
                        tf = 1 + math.log(fdist[word]) / log_max_freq
                        idf = 1 + math.log(len(keysen) / wordfreq)
                        senvec[word] = tf * idf
                    else:
                        senvec[word] = (1 + math.log(2.0 * fdist[word])) * math.log(2.0 * len(keysen) / wordfreq)
                else:
                    senvec[word] = 0
            sentence['StuSVec'] = senvec
        debug_print("Answer.SentenceAnalysis(%s,_) => %s" % (str(fulltext), str(ans_sentencelist)), level=6)
        debug_print("\t_ [textfdist]: %s" % str(textfdist), level=7)
        return ans_sentencelist


    # CalCosDist(answer_sentence_list, standard_sentence): Calculates the cosine distance between
    # each of the terms vectors representing the student's ANSWER_SENTENCE_LIST and the teacher's
    # STANDARD_SENTENCE.
    # Reurns maximum cosine distance for the sentences, along with corresponding sentence.
    # Note: Cosine theta = a . b / |a| * |b|, where theta is the angle between vectors a and b,
    # a . b is their dot product, and |v| is vector length:
    #    http://en.wikipedia.org/wiki/Cosine_similarity
    #
    # EX: ans.CalCosDist([{'StuS': 'The lawyer chased the vehicle.', 'No': 1, 'StuSVec': {'chased': 1.1736001944781467, 'lawyer': 2.3472003889562933, 'vehicle': 1.1736001944781467}, 'StuWords': ['lawyer', 'chased', 'vehicle']}, {'StuS': 'The vehicle chased back.', 'No': 2, 'StuSVec': {'chased': 1.1736001944781467, 'lawyer': 0, 'vehicle': 1.1736001944781467}, 'StuWords': ['vehicle', 'chased', 'back']}], {'TotalS_No': [1], 'SenWords': ['attorney', 'chased', 'ambulance'], 'No': 1, 'KeyS': ' The attorney chased the ambulance.', 'Point_No': 'P1', 'KeyBVec': [], 'KeySVec': {'attorney': 2.3472003889562933, 'chased': 1.1736001944781467, 'ambulance': 1.1736001944781467}}) => (0.70710678118654757, {'StuS': 'The vehicle chased back.', 'No': 2, 'StuSVec': {'chased': 1.1736001944781467, 'lawyer': 0, 'vehicle': 1.1736001944781467}, 'StuWords': ['vehicle', 'chased', 'back']})
    #
    def CalCosDist(self, ans_sentencelist, std_sen):
        debug_print("Answer.CalCosDist%s" % str((ans_sentencelist, std_sen)), level=6)
        match_sen = None
        max_cos = 0
        apply_term_expansion = (self.apply_synonym_expansion or self.apply_ancestor_expansion)
        all_std_words = std_sen['KeySVec'].keys()
        for stu_sen in ans_sentencelist:
            # Make sure student sentence not already matched
            # TODO: Rework the already-matched check to be in terms of words not sentences (e.g., in case student just gives one long sentence).
            if (self.only_match_sentence_once and stu_sen.has_key('Selected')):
                debug_print("Ingoring already matched sentence %s" % stu_sen['No'])
                continue
            # Compute measure for current sentence
            q, s, qs = 0, 0, 0
            exp_terms = []
            for word in all_std_words:
                # OLD: q += std_sen['KeySVec'][word] * std_sen['KeySVec'][word]
                # OLD: s += stu_sen['StuSVec'][word] * stu_sen['StuSVec'][word]
                # OLD: qs += std_sen['KeySVec'][word] * stu_sen['StuSVec'][word]

                # If a standard word doesn't occur in the student sentence, then apply term expansion
                # by checking for most frequent synonym and/or ancestor term that does occur.
                # Note: Ancestor terms might be too general, so not checked if synonym found.
                # Also, expansions omit standard terms to avoid counting evidence twice.
                # TODO: Scale ancestor weight by degree of generality.
                std_freq = std_sen['KeySVec'][word]
                stu_freq = stu_sen['StuSVec'][word] if stu_sen['StuSVec'].has_key(word) else 0
                std_word = word
                if ((stu_freq == 0) and apply_term_expansion):
                    stu_word = std_word
                    scale_factor = 1.0
                    # Check synonyms (e.g., attorney for lawyer), excluding words in standard
                    if (self.apply_synonym_expansion):
                        debug_print("Checking for synonym of standard term '%s' among student terms" % std_word, level=5)
                        synonyms = list_difference(wordnet.get_synonyms(std_word), all_std_words)
                        exp_word = find_most_freq_term(synonyms, stu_sen['StuSVec'])
                        if (exp_word and (exp_word != stu_word)):
                            # Note: Uses frequency from student vector for synonym term
                            stu_word = exp_word
                            scale_factor = self.synonym_scale_factor
                            debug_print("Using (student) synonym '%s' to match (standard) word '%s'" % (exp_word, std_word), level=4)
                    # Check ancestors (e.g., professional for lawyer), excluding words in standard
                    if (self.apply_ancestor_expansion and (stu_word == std_word)):
                        debug_print("Checking for ancestor of standard term '%s' among student terms" % std_word, level=5)
                        ancestors = list_difference(wordnet.get_hypernym_terms(std_word, self.max_ancestor_links), all_std_words)
                        exp_word = find_most_freq_term(ancestors, stu_sen['StuSVec'])
                        if (exp_word and (exp_word != stu_word)):
                            # As before, uses frequency from student vector for expansion term
                            stu_word = exp_word
                            scale_factor = self.synonym_scale_factor
                            debug_print("Using (student) ancestor term '%s' to match (standard) word '%s'" % (exp_word, std_word), level=4)
                    # Update frequency and make note of expansion for posthoc diagnosis
                    if (stu_word != std_word):
                        stu_freq = stu_sen['StuSVec'][stu_word] * scale_factor
                        debug_print("Scaled frequency score from %f to %f" % (stu_sen['StuSVec'][stu_word], stu_freq), level=7)
                        exp_terms.append(std_word + "->" + stu_word)
                # Do component-wise update
                debug_print("deltas: q=%f s=%f qs=%f" % (std_freq * std_freq, stu_freq * stu_freq, std_freq * stu_freq),level=6)
                q += std_freq * std_freq
                s += stu_freq * stu_freq
                qs += std_freq * stu_freq
                debug_print("q=%f s=%f qs=%f" % (q, s, qs),level=7)
            if q == 0 or s == 0:
                qs_cos = 0
            else:
                qs_cos = qs / (math.sqrt(q * s))
            if (apply_term_expansion):
                stu_sen['ExpTerms'] = exp_terms

            # Update max score, optionally recording expansion terms in hash for matching student sentence (under ExpTerms)
            stu_words = [word for word in stu_sen['StuSVec'] if stu_sen['StuSVec'][word] > 0]
            if qs_cos > max_cos and len(stu_words) > 0:
                max_cos = qs_cos
                match_sen = stu_sen
        if (self.only_match_sentence_once and match_sen):
            match_sen['Selected'] = True
        debug_print("Answer.CalCosDist(%s,_) => %s" % (str(ans_sentencelist), str((max_cos, match_sen))), level=6)
        return max_cos, match_sen


    # Mark(key_sentences, key_point_info, , answer_sentences): Mark the student ANSWER_SENTENCES against teacher KEY_SENTENCES,
    # for questions indicated by KEY_POINT_INFO.
    # Returns the list of points that are considered as been answered correctly.
    #
    # EX: ans.Mark([{'TotalS_No': [1], 'SenWords': ['attorney', 'chased', 'ambulance', 'downtown'], 'No': 1, 'KeyS': ' The attorney chased the ambulance downtown.', 'Point_No': 'P1', 'KeyBVec': [], 'KeySVec': {'downtown': 2.3472003889562933, 'attorney': 2.3472003889562933, 'chased': 1.1736001944781467, 'ambulance': 1.1736001944781467}}, {'TotalS_No': [2], 'SenWords': ['ambulance', 'chased'], 'No': 2, 'KeyS': ' The ambulance chased back.', 'Point_No': 'P2', 'KeyBVec': [], 'KeySVec': {'downtown': 0, 'attorney': 0, 'chased': 1.1736001944781467, 'ambulance': 1.1736001944781467}}], ['P1', 'P2'], [{'StuS': 'The lawyer chased the vehicle downtown.', 'No': 1, 'StuSVec': {'downtown': 2.3472003889562933, 'chased': 1.1736001944781467, 'lawyer': 2.3472003889562933, 'vehicle': 1.1736001944781467}, 'StuWords': ['lawyer', 'chased', 'vehicle', 'downtown']}, {'StuS': 'The vehicle chased back.', 'No': 2, 'StuSVec': {'downtown': 0, 'chased': 1.1736001944781467, 'lawyer': 0, 'vehicle': 1.1736001944781467}, 'StuWords': ['vehicle', 'chased', 'back']}]) => ['P1', 'P2']
    #
    def Mark(self, std_sentencelist, std_pointlist_no, ans_sentencelist):
        debug_print("Answer.Mark%s" % str((std_sentencelist, std_pointlist_no, ans_sentencelist)), level=99)
        detailedmarklist = []
        marklist = []
        # Check each of the teacher key sentences
        for point_no, std_sen in zip(std_pointlist_no, std_sentencelist):
            if 'P0.' in point_no:
                continue
            std_senlist = []
            stu_senlist = []
            keyword_num = 0
            keyword_sum = 0
            sen_match = 0
            len_match = 0
            std_senlist = std_sen['KeyS'].split('.')
            keyword_sum += len(std_sen['KeyBVec'])
            # Calculate distance max between any of the student answer sentences and the key sentence
            max_cos, match_sen = self.CalCosDist(ans_sentencelist, std_sen)
            if max_cos > self.dist_threshold:
                sen_match += max_cos
                len_match += 1
                # Check for matches against specified keywords
                if std_sen['KeyBVec']:
                    # TODO: Include synonym check for keyword (ancestor check would likely be too approximate)
                    keyword_freq = sum(1 for keyword in std_sen['KeyBVec']
                                       if keyword.lower() in match_sen['StuS'].lower())
                    keyword_num += keyword_freq
                    keyword_match = 1.0 * keyword_freq / len(std_sen['KeyBVec'])
                else:
                    keyword_match = None
                stu_senlist.append({'StdNo': std_sen['No'],
                                    'Max_Match': std_sen.get('TotalS_No'),
                                    'Stu': match_sen['StuS'], 'Mat_Deg': max_cos,
                                    'Keyword_Match': keyword_match})

            # Caluculate factors of mark due to keyword matching and having multiple sentence matches
            if std_senlist and len_match:
                keyword_rate = 1.0 * keyword_num / keyword_sum if keyword_sum > 0 else 0
                sen_rate = 1.0 * sen_match
                ## OLD: #sen_rate = 1.0 * sen_match / math.log(len(std_senlist) + 1)
                #moderate
                sen_rate_match = 1.0 * sen_match / len_match if (1.0 * len_match / len(std_senlist) > self.multisen_matchrate) and len(std_senlist) > 1 else 0
                #loose
                #sen_rate_match = 1.0 * sen_match / len_match if (1.0 * len_match / len(std_senlist) > self.multisen_matchrate) and len(std_senlist) > 1 else 0
                # TPO: same as moderate
            else:
                sen_rate = 0
                sen_rate_match = 0
                keyword_rate = 0

            # Trace out current state (based on Xiangguandu Juzi's commented out print code)
            if (__debug__ and (debugging_level() > 2)):
                debug_print("Point_No: " + str(point_no))
                debug_print('stdsen: %s --- %s' % (str(std_sen['No']), str(std_sen['KeyS'])))
                debug_print('stdvec: ' + str(std_sen['KeySVec']))
                debug_print('Max Relevance: ' + str(sen_rate))
                if match_sen:
                    debug_print('stusen: %s --- %s' % (str(match_sen['No']), str(match_sen['StuS'])))
                    debug_print('stuvec: ' + str(match_sen['StuSVec']))
                    debug_print('Relevant Keyword: ' + str([word for word in match_sen['StuSVec'] if match_sen['StuSVec'][word] > 0]))
                    # Optionally show words used during term expansion
                    # TODO: Track down when not defined
                    if (self.apply_synonym_expansion or self.apply_ancestor_expansion):
                        ## OLD: debug_print('expansion terms: ' + str(match_sen['ExpTerms']))
                        exp_terms = match_sen['ExpTerms'] if match_sen.has_key('ExpTerms') else []
                        debug_print('expansion terms: ' + str(exp_terms))
                else:
                    debug_print('stusen/stuvec/Relevant Keyword: n/a')

            # Add to current list of marks
            detailedmarklist.append({'Point_No': point_no,
                                     'Std_senList': std_senlist,
                                     'Stu_SenList': stu_senlist,
                                     'Keyword_Rate': keyword_rate,
                                     'Sentence_Rate': sen_rate,
                                     'Sentence_Rate_Match': sen_rate_match})
        # Return list of points above thresholds
        # TODO: See why keyword rate is not considered
        marklist = list(point['Point_No'] for point in detailedmarklist
                        if point['Sentence_Rate'] > self.sen_threshold
                        or point['Sentence_Rate_Match'] > self.multisen_threshold)
        debug_print("Answer.Mark(_,_,%s) => %s" % (str(ans_sentencelist), str(marklist)), level=6)
        return marklist


    # Comparison(point-list, grading-rules): Determines the grade for POINT-LIST based on grading RULES.
    #
    # EX; ans.Comparison(['P1'], [{'Mark': 10, 'Point': ['P1', 'P2']}, {'Mark': 5, 'Point': ['P1']}, {'Mark': 5, 'Point': ['P2']}]) => (5, ['P1'])
    # TODO: Rename to something more indicative of the function's behavior (e.g., DetermineGrade)
    #
    def Comparison(self, marklist, rulelist):
        match = True
        for rule in rulelist:
            # First first rule in which all correctly marked points occur
            for point in rule['Point']:
                if point not in marklist:
                    match = False
            # Return result mark score and rule if found
            if match:
                debug_print("Answer.Comparison(%s, %s) => %s" % (marklist, rulelist, str((rule['Mark'], rule['Point']))), level=6)
                return rule['Mark'], rule['Point']
            else:
                match = True
        debug_print("Answer.Comparison(%s, %s) => %s" % (marklist, rulelist, str((0, None))), level=6)
        return 0, None


    # Omitted(correct-points, point-info, rules): Evaluates grading RULES to determine grade for CORRECT-POINTS and
    # returns the grade along with the list with the question text from POINT-INFO prefixed with C if correct or W if incorrect.
    #
    # EX: ans.Omitted(['P1'], [{'Point_No': 'P1', 'Point_Text': ' The attorney chased the ambulance downtown. '}, {'Point_No': 'P2', 'Point_Text': ' The ambulance chased back. '}], [{'Mark': 10, 'Point': ['P1', 'P2']}, {'Mark': 5, 'Point': ['P1']}, {'Mark': 5, 'Point': ['P2']}]) => (10, ['C1 The attorney chased the ambulance downtown. ', 'W2 The ambulance chased back. '])
    # TODO: Rename to something more indicative of the function's behavior (e.g., EvaluatePointRules)
    #
    def Omitted(self, marklist, std_pointlist, rulelist):
        debug_print("Answer.Omitted%s" % str((marklist, std_pointlist, rulelist)), level=99)
        mark, rule = self.Comparison(marklist, rulelist)
        omitted = []
        for point in std_pointlist:
            if 'P0.' not in point['Point_No']:
                if point['Point_No'] in marklist:
                    omitted.append('C' + point['Point_No'][1:] + point['Point_Text'])
                else:
                    omitted.append('W' + point['Point_No'][1:] + point['Point_Text'])
        debug_print("Answer.Omitted(_,_,_) => %s" % str((mark, omitted)), level=6)
        return mark, omitted


    # Analysis(answer_text, global_freq_dist, key_sentences, points, grading_rules): First preprocesses the student
    # ANSWER_TEXT by breaking it into  sentences, tokenizing them into words, computing term
    # vectors (based on GLOBAL_FREQ_DIST), and then weighting the vectors using a TF/IDF-style scheme. 
    # Then, the vectors for the student sentences are compared against those for the similarly preprocessed
    # KEY_SENTENCES (see Standard.Analysis), and those matching specific question POINTS are graded according to 
    # GRADING_RULES.
    #
    # EX: ans.Analysis('  The lawyer chased the vehicle downtown.\n  The vehicle chased back.\n',     <FreqDist with 4 samples and 6 outcomes>,     [{'TotalS_No': [1], 'SenWords': ['attorney', 'chased', 'ambulance', 'downtown'], 'No': 1, 'KeyS': ' The attorney chased the ambulance downtown.', 'Point_No': 'P1', 'KeyBVec': [], 'KeySVec': {'downtown': 2.3472003889562933, 'attorney': 2.3472003889562933, 'chased': 1.1736001944781467, 'ambulance': 1.1736001944781467}}, {'TotalS_No': [2], 'SenWords': ['ambulance', 'chased'], 'No': 2, 'KeyS': ' The ambulance chased back.', 'Point_No': 'P2', 'KeyBVec': [], 'KeySVec': {'downtown': 0, 'attorney': 0, 'chased': 1.1736001944781467, 'ambulance': 1.1736001944781467}}],     [{'Point_No': 'P1', 'Point_Text': ' The attorney chased the ambulance downtown. '}, {'Point_No': 'P2', 'Point_Text': ' The ambulance chased back. '}],     [{'Mark': 10, 'Point': ['P1', 'P2']}, {'Mark': 5, 'Point': ['P1']}, {'Mark': 5, 'Point': ['P2']}])
    # TODO: Correct callers to base the global_freq_dist argument on the answer text not standard (see tests.ty and ../student/views.py).
    #
    def Analysis(self, fulltext, textfdist, std_sentencelist, std_pointlist, rulelist):
        debug_print("Answer.Analysis%s" % str((fulltext, textfdist, std_sentencelist, std_pointlist, rulelist)), level=99)
        if not fulltext or not textfdist or not std_sentencelist or not std_pointlist or not rulelist:
            debug_print("Answer.Analysis(_,_,_,_,_) => %s" % str((None, None, None)), level=6)
            return None, None, None
        ans_sentencelist = self.SentenceAnalysis(fulltext, textfdist)
        std_pointlist_no = list(point['Point_No'] for point in std_pointlist)
        marklist = self.Mark(std_sentencelist, std_pointlist_no, ans_sentencelist)
        mark, omitted = self.Omitted(marklist, std_pointlist, rulelist)
        debug_print("Answer.Analysis(_,_,_,_,_) => %s" % str((mark, marklist, omitted)), level=6)
        return mark, marklist, omitted

#------------------------------------------------------------------------

# ImageAnswer: Class for students answers regarding images
#
# NOTE: This is not used by the algorithm proper, but it is used in other components
# (e.g., ../student/views.py).
#

class ImageAnswer(object):

    def __init__(self,):
        debug_print("ImageAnswer()", level=6)
        self.logger = logging.getLogger(__name__)

    def Comparison(self, marklist, rulelist):
        match = True
        for rule in rulelist:
            for point in rule['Point']:
                if point not in marklist:
                    match = False
            if match:
                debug_print("ImageAnswer.Comparison(%s, %s) => %s" % (marklist, rulelist, str((rule['Mark'], rule['Point']))), level=6)
                return rule['Mark'], rule['Point']
            else:
                match = True
        debug_print("ImageAnswer.Comparison(%s, %s) => %s" % (marklist, rulelist, str((0, None))), level=6)
        return 0, None

    def Omitted(self, marklist, std_pointlist, rulelist):
        mark, rule = self.Comparison(marklist, rulelist)
        omitted = []
        for point in std_pointlist:
            if 'P0.' in point['Point_No']:
                if point['Point_No'] in marklist:
                    omitted.append('C' + point['Point_No'][1:] + point['Point_Text'])
                else:
                    omitted.append('W' + point['Point_No'][1:] + point['Point_Text'])
        debug_print("ImageAnswer.Omitted(_,_,_) => %s" % str((mark, omitted)), level=6)
        return mark, omitted

    def Analysis(self, imgpoints, std_pointlist, rulelist):
        if imgpoints:
            marklist = list(imagepoint['Point_No'] for imagepoint, stuansimage in imgpoints)
            mark, omitted = self.Omitted(marklist, std_pointlist, rulelist)
            debug_print("ImageAnswer.Analysis(_,_,_) => %s" % str((mark, marklist, omitted)), level=6)
            return mark, marklist, omitted
        debug_print("ImageAnswer.Analysis(_,_,_) => None", level=6)

#------------------------------------------------------------------------

# If invoked standalone, show simple hard-coded example (see tests.py for detailed examples).
# TODO: Straighten out convoluted invocation sequence (bowl of spaghetti module inter-dependencies).
#
if __name__ == '__main__':
    # Specify input texts and grading scheme
    key_full_text = "1 . The attorney chased the ambulance.\n2 . The ambulance chased back.\n"
    stu_full_text = "1. Lawyers practice law.\n2 . The lawyer chased the vehicle.\n3 . The vehicle chased back.\n"
    scheme = [("all", 10), ("only P1 or P2", 5)]

    # Do initialization
    from standard import *
    from markscheme import *
    ans = Answer()
    std = Standard()

    # Analyze key and expand the rule template
    pointlist, key_freq_dist, key_sentencelist = std.Analysis(key_full_text)
    stu_full_text_proper = re.sub(r"\d+\s\.", " ", stu_full_text)
    #
    print "Input:\n\nKey: %s\nScheme: %s\nStudent: %s\n" % (key_full_text, str(scheme), stu_full_text)
    text_pointlist = [point['Point_No'] for point in pointlist if 'P0.' not in point['Point_No']]
    ms = MarkScheme(text_pointlist)
    rulelist = [r for r in ms.GetRules(scheme)]

    # Get frequency distribution for answer text words
    # Note: Ignores the resulting point list and sentence decomposition.
    stu_pointlist, stu_freq_dist, stu_sentencelist = std.Analysis(stu_full_text)

    # Do the answer analysis and show the result
    # Note: The frequency distribution needs to be done over the question for term expansion to work.
    ## BAD: mark, marklist, omitted = ans.Analysis(stu_full_text_proper, key_freq_dist, key_sentencelist, pointlist, rulelist)
    mark, marklist, omitted = ans.Analysis(stu_full_text_proper, stu_freq_dist, key_sentencelist, pointlist, rulelist)
    print "Result:\n\nMark: %s\nList: %s\nOmitted: %s" % (str(mark), str(marklist), str(omitted))
    debug_print("stop algo/answer.py: " + debug_timestamp())
