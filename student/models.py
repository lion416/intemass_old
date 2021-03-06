from django.db import models
from intemass.portal.models import SProfile
from intemass.question.models import Question, QuestionImage, QuestionVideo
from django.utils.timezone import now


class StudentAnswer(models.Model):
    student = models.ForeignKey(SProfile)
    sentencelist = models.TextField(null=True, blank=True)
    mark = models.IntegerField(default=0)
    timestamp = models.DateTimeField('time taked', default=now)
    pointmarklist = models.TextField(null=True, blank=True)
    omitted = models.TextField(null=True, blank=True)
    html_answer = models.TextField(null=True, blank=True)
    txt_answer = models.TextField(null=True, blank=True)
    question = models.ForeignKey(Question)
    timeleft = models.IntegerField(default=-1)
    taked = models.BooleanField(verbose_name=u'Question Taked')
    stuansimages = models.ManyToManyField(QuestionImage, verbose_name=u'stuansimages')
    grammar_issues = models.TextField(null=True, blank=True)
    closeness = models.FloatField(default=0.0)
    feedback = models.TextField(max_length=255)
    feedback_code = models.TextField()
    attempted_count = models.IntegerField(default=0)

    def __unicode__(self):
        return u'StudentAnswerSheet_' + str(self.question.qname) + u'_' + self.student.user.username + '-----' + str(self.id)
