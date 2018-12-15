/*
 * yanchao727@gmail.com
 * 15/06/2012
 *
 */

function popMessage()
{ 
	$( "#dialog-message" ).dialog('open');
} 

$(document).ready(function(){
	console.log('popMessage();');
	$( "#dialog-message" ).dialog({
		modal: true,
		autoOpen: false,
		buttons: { 
		Result: function(){
			$(this).dialog('close');
			$("#btnGoToReport").click();
		}
		},
		
	});
	$('input[name=question_multiselection_option]').customInput();
	console.log($('input[name=question_multiselection_option]'));
});


var nmwidth = 1330;
var nmheight = 700;

var nmopts = {
        sizes: { 
            initW: nmwidth,
            initH: nmheight,
            w: nmwidth,
            h: nmheight,
            minW: nmwidth,
            minH: nmheight
        },
        callbacks: {
            beforeShowCont: function() {
                var structure = $('.nyroModalCont');
                var iframe = $('.nyroModalCont iframe');
                nmwidth = structure.width();
                nmheight = structure.height();
                iframe.css('width', nmwidth).css('height', nmheight);
            }
        }
    };



function setAllNyroModal()
{
	
}
function onGraphicClicked(objectID, optionid)
{
	$("#" + objectID).select2("val",[]);
	console.log('onGraphicClicked:',objectID , optionid);
	questioncanvas_bindnm(optionid,objectID);

	
}
 
	


var stuthumbnail_ids = '';
function onCloseExamGotoReport( PaperID,stuID)
{
	var paperids = [];
	paperids.push("{pid:" + PaperID + ", stuid:" + stuID + "}");
	$('#paperids').val(paperids);
	 document.formx1.submit();


}
function onChangedOptionList(questionID, optionID)
{ 
	$("#selected_diagrams li img").each(function(){
		stuthumbnail_ids += $(this).attr("id") + ",";
	});
	if (stuthumbnail_ids !== ''){
		stuthumbnail_ids = stuthumbnail_ids.substring(0, stuthumbnail_ids.length - 1);
	}
	console.log('questionid', questionID  , 'optionID', optionID, 'stuthumbnail_ids', stuthumbnail_ids
		,"optionID:", optionID);
	var strURLSelectOption = "";
	if(global_isRetake)
	{
		strURLSelectOption = "/mcq/student/selectedoption_retakepaper/";
	}
	else
	{
		strURLSelectOption = "/mcq/student/selectedoption/";
	}
	$.ajax({type: "POST",
	    url: strURLSelectOption,
	    dataType: "json",
	    data: {
		"questionid": questionID, 
		"stuthumbnail_ids": '',
		"optionID": optionID,
		"paperid": paperid,
		"csrfmiddlewaretoken": csrfvalue,
	    },
	    success: function(payload){
		console.log('payload',payload);
		$('input[name=question_multiselection_option]').attr('disabled','true');
		if(payload['state'] == 'success')
		{
			console.log("option sent successful");
			$("#next").click();
		
		}
		else{
			intemass.ui.showclientmsg(payload['message']);
		}
		//getProcessDialog().dialog('close');
	    },
	    error: function(MLHttpRequest, textStatus, errorThrown){
		console.log("submitpaper success/error: " + "; " + errorThrown + "; " + MLHttpRequest);

		console.log('error on select option');
	    }
	});
	$( this ).dialog( "close" );


	
}


$(function(){
	
});
;(function($, undef) {

    // OLD: var timeoutTimer = setInterval(refreshtimeout, 60000);
    var timeoutTimer = setInterval(refreshtimeout, 300000);
    var config = {
        toolbar: [],
        height: 200,
        toolbarStartupExpanded: false,
        readOnly: true
    };
	var configOption = {
		toolbar: [],
		height: 150,
		toolbarStartupExpanded: false,
		readOnly: true
	    };


    var nmwidth = 1330;
    var nmheight = 700;
    var nmopts = {
        sizes: { 
            initW: nmwidth,
            initH: nmheight,
            w: nmwidth,
            h: nmheight,
            minW: nmwidth,
            minH: nmheight
        },
        callbacks: {
            beforeShowCont: function() {
                var structure = $('.nyroModalCont');
                var iframe = $('.nyroModalCont iframe');
                nmwidth = structure.width();
                nmheight = structure.height();
                iframe.css('width', nmwidth).css('height', nmheight);
            }
        }
    };


    $(function(){
	console.log("i'm here ");
        $("#question_name_show").text(qnames[0]);
        $("#question_process_show").text(1 + "/" + qids.length);
        ////$("#question_editor").ckeditor(config);
	$("textarea").ckeditor(config);
	//$('#optionlist_option0').nextUntil('#optionlist_option100').ckeditor(config);
        loadquestion(qids[0]);
        pullThumbnails(qids[0]);
        $("#answer_editor").ckeditor();
        
        refreshtimeout();
        $(window).bind('beforeunload', function(e){
		var strURLCheck = "";
		if(global_isRetake)
		{
			strURLCheck = "/mcq/student/checktime_retake/";
		}
		else
		{
			strURLCheck = "/mcq/student/checktime/";			
		}
            $.post(strURLCheck,
                {
                    'save': true,
                    'paperid': paperid,
                    'csrfmiddlewaretoken': csrfvalue
                },
                function(payload) {
                    console.log('time saved');
            },'json');
        }); 

        var count = qids.length -1;
        var i = 0;
        $("#previous").click(function(){
            //submitanswer(qids[i]);
            if(i !== 0){
                i -= 1;
                $("#answer_editor").val("");
                $("#question_name_show").text(qnames[i]);
                $("#question_process_show").text(i+1+"/"+qids.length);
                loadquestion(qids[i]);
                pullThumbnails(qids[i]);
            }
        });
	
	var setSelectedOptionList = function(){
		var selected_optionlist = $('input[name=question_multiselection_option]:checked').val();
		if(selected_optionlist==null)
		{
			console.log('nothing here..is null');
		}
		else
		{
			console.log('selected', selected_optionlist);
		}
		
	};
	$("#next").click(function(){

		setSelectedOptionList();
		console.log('next clicked');
		//submitanswer(qids[i]);
		console.log("i:",i,", Count: " , count);
		if((i   ) != count  ){
			i += 1;
			$("#answer_editor").val("");
			$("#question_name_show").text(qnames[i]);
			$("#question_process_show").text(i+1+"/"+qids.length);
			loadquestion(qids[i]);
			pullThumbnails(qids[i]);
		}
		else
		{
			
			if((i  ) ==count ){
				$("#btnGoToReport").css("display", "block");
				popMessage();
			}
		}
	});

        $("#first").click(function(){
            //submitanswer(qids[i]);
            $("#answer_editor").val("");
            $("#question_name_show").text(qnames[0]);
            $("#question_process_show").text(1+"/"+qids.length);
            loadquestion(qids[0]);
            pullThumbnails(qids[0]);
            i = 0;
        });

        $("#last").click(function(){
            //submitanswer(qids[i]);
            $("#answer_editor").val("");
            $("#question_name_show").text(qnames[count]);
            $("#question_process_show").text(count+1+"/"+qids.length);
            loadquestion(qids[count]);
            pullThumbnails(qids[count]);
            i = count;
		    $("#btnGoToReport").css("display", "block");
			popMessage();
        });
	$("#btnBack").click(function(){
		console.log('back is clicked');
		window.location.href = "/mcq/student/index/";
	});
        $("#submit1").click(function(){
            submitpaper(qids[i], paperid);
        });

        // resolve the icons behavior with event delegation
        /* $("ul.gallery > li").click(function(event) {
            var $item = $( this );
            var $target = $( event.target );

            if ($target.is("a.ui-icon-check")){
                selectImage($item);
            }else if ($target.is("a.ui-icon-zoomin")){
                viewLargerImage( $target );
            }else if ($target.is("a.ui-icon-closethick")){
                unselectImage($item);
            }
            return false;
        });*/
    });

    var answercanvas_bindnm;
    answercanvas_bindnm = function(questionid, stuanswerid) {
	console.log('answercanvas_bindnm');
        $(".Graphic").click(function() {
		console.log('is it this one?');
            var canvasurl = '/canvas/?canvasname=' +  $(this).text() + '&questionid=' + questionid + '&stuanswerid=' + stuanswerid + '&view=undefined';
		console.log('using this?, ' , canvasurl);
            $(this).attr({
                'class': 'nyroModal',
                'href': canvasurl,
                'target': '_blank'
            });
            $(this).nm(nmopts);
            $(this).next().attr({
                'onclick': function () {
                    return false;
                }
            });
        });
    };

var  questioncanvas_bindnm = function(){
	//var test = $("#optionlist_canvas0"); // document.getElementById("question_canvas")
	//var questionid = 1;
	//' +  $(this).text() + uid + '
	//var canvasurl =  '/mcq/canvas/?canvasname=1&questionid=' + questionid  ; 
	//console.log('canvasurl:' , canvasurl);
	//test.attr("class","nyroModal populate greenBtn");
	//test.attr("href", canvasurl)
	//test.attr("target", "_blank")
		var test = document.getElementById("question_canvas")
		//' +  $(this).text() + uid + '
		var canvasurl =  '/mcq/canvas/?canvasname=1&questionid=' + global_questionID + '&view=' + ''; 
		console.log('canvasurl:' , canvasurl);
		test.setAttribute("class","nyroModal populate greenBtn");
		test.setAttribute("href", canvasurl)
		test.setAttribute("target", "_blank")
		$("#question_canvas").unbind('click').click(function(event){
			    $("#question_canvas").off();
			    width: "copy"
			    tokenSeparators: [",", " "]
			    event.preventDefault()
			    $(this).nm(nmopts);
				$(this).next().attr({
						'onclick': function () {
							return false;
						}
					});
			    $.ajax({
				url: $("#question_canvas").attr("href") ,
				success: function (resp) {
						$("#question_canvas").trigger('click');
					},
				error: function(e){
						alert('Error:');
					}  
			    });
			});
		


		$( ".Graphic" ).each(function( index ) {
			var strID ="#" +  $(this).attr("id");
			$(strID).unbind('click').click(function(event){
			    $(strID).off();
			    width: "copy"
			    tokenSeparators: [",", " "]
			    event.preventDefault()
			    $(this).nm(nmopts);
				$(this).next().attr({
						'onclick': function () {
							return false;
						}
					});
			    $.ajax({
				url: $(strID).attr("href") ,
				success: function (resp) {
						$(strID).trigger('click');
					},
				error: function(e){
						alert('Error:');
					}  
			    });
			});
		});
	
	};
	








    var initcanvasarea = function(){
	console.log('initcanvasarea ');
        $(".Graphic").select2('val',[]);
	$("question_canvas").select2('val',[]);
	questioncanvas_bindnm();	
    };

    var getProcessDialog = function(){

        var processing_dialogue = $( "#dialog-process" ).dialog({
            autoOpen: false,
            resizable: false,
            height:150,
            width:550,
            modal: true
        });

        $("#progressbar").progressbar({
            value: 100 
        });
        return processing_dialogue;
    };

    

    var submitpaper = function(questionid, paperid){
        getProcessDialog().dialog('open');
        answer_html = $("#answer_editor").val();
        $("#selected_diagrams li img").each(function(){
            stuthumbnail_ids = $(this).attr("id");
        });
        $.ajax(
            {
                type: "POST",
                url: "/student/submitanswer/",
                dataType: "json",
                data: {
                    "answer_html": answer_html, 
                    "stuthumbnail_ids": stuthumbnail_ids,
                    "csrfmiddlewaretoken": csrfvalue,
                    "questionid": questionid,
            },
            success: function(payload){
		console.log("submitpaper success");
                $.ajax(
                    {
                        type: "POST",
                        url: "/student/submitpaper/",
                        dataType: "json",
                        data: {
                            "paperid": paperid,
                            'csrfmiddlewaretoken': csrfvalue
                    },
                    success: function(payload){
			console.log("submitpaper success/success");
                        getProcessDialog().dialog('close');
                        if(payload['state'] === 'passed'){
                            gotosummarize(paperid, true);
                        }else if (payload['state'] === 'failed'){
                            gotosummarize(paperid, false);
                        }
                    },
                    error: function(MLHttpRequest, textStatus, errorThrown){
			console.log("submitpaper success/error: " + "; " + errorThrown + "; " + MLHttpRequest);
                        getProcessDialog().dialog('close');
                        }
                });
            },
            // OLD: error: function(MLHttpRequest, textStatus, errorThrown){}
	    error: function(MLHttpRequest, textStatus, errorThrown){
		console.log("submitpaper error: " + textStatus + "; " + errorThrown + "; " + MLHttpRequest);
                getProcessDialog().dialog('close');
	    }
        });
    };
var global_questionID = 0;

    /// This is to retrieve option list;
    var loadquestion = function(questionid){
	global_questionID = questionid;
	var strURL_StudentGet = "";
	if( global_isRetake)
	{
		strURL_StudentGet = "/mcq/question/stu_retake_get/";
	}
	else{
		strURL_StudentGet = "/mcq/question/stuget/";
	}
        if(questionid != -1){
            $.post(strURL_StudentGet ,
            {
                'questionid': questionid,
                'csrfmiddlewaretoken': csrfvalue,
		'paperid':paperid
            },
            function(payload){
		//console.log(payload);
		//minhong
                if(payload.state === "success"){
		    i=1;
                    var retake = intemass.util.getUrl('retake');
                    $("#question_editor").val(payload['question_content']);
                    if(!retake){
                        $("#answer_editor").val(payload['question_stuanswer']);
                    }
			console.log("this is the multiselect",payload['question_multiselection']);

			$("#question_multiselection").html(payload['question_multiselection']);
			bindImageIconClick();
			initcanvasarea();


			

			 //$("#question_canvas").select2("val", question_canvas_name);
                }
		$( "textarea" ).each(function( index ) {
			if (CKEDITOR.instances[$(this).attr("id")]) {
			    CKEDITOR.remove(CKEDITOR.instances[$(this).attr("id")]);
			}
		});
		$("textarea").ckeditor(configOption);
		//setAllNyroModal();
            },
            'json');
        }
    };

    var pullThumbnails = function(questionid){
	console.log('call here pullThumbnails');
        $.post("/mcq/question/studentthumbnails/",
        {
            'questionid': questionid,
            'csrfmiddlewaretoken': csrfvalue
        },
        function(payload) {
            if(payload.state === "success"){
                thumbnails = payload['thumbnails'];
                stuthumbnails = payload['stuthumbnails'];
		console.log('stuthumbnails', stuthumbnails);
		console.log('thumbnails', thumbnails);
                thumbhtml = makeimagethumbnailhtml(thumbnails, false);
                stuthumbhtml = makeimagethumbnailhtml(stuthumbnails, true);
                var $list = $("ul", $("#thumbnails"));
                $("#thumbnails li").remove();
		console.log("$list: " , $list);
                $(thumbhtml).appendTo($list);
                $list = $( "ul", $("#stuthumbnails"));
                $("#stuthumbnails li").remove();
                $(stuthumbhtml).appendTo($list);
                bindImageIconClick();
            }
        }, 'json');
    };


    var makeimagethumbnailhtml = function(thumbnails, selected){
	console.log('thumbnails:' , thumbnails);
	console.log('selected:' , selected);
        var thumbhtml = '';
        for (var t in thumbnails){
		console.log(" makeing thumbnails " , t);
            thumbhtml += '<li class="ui-widget-content ui-corner-tr">';
            thumbhtml += '<h6 class="ui-widget-header">' + thumbnails[t][1].slice(0,5) + '...' + '</h6>';
            thumbhtml += '<img src="/static/' + thumbnails[t][0] + '" id=' + thumbnails[t][3] +' alt="' + thumbnails[t][1] + '" width="96" height="72"></img>';
            thumbhtml += '<a href="#" title="View Larger Image" class="ui-icon ui-icon-zoomin">View Larger</a>';
            
        }
        return thumbhtml;
    };


    var bindImageIconClick = function(){
	console.log('ok...bindImageIconClick');
        var $imagesfrom = $( "#possible_diagrams" );
        var $imagesto = $( "#stuthumbnails" );

        /*$( "li", $imagesfrom ).draggable({
            cancel: "a.ui-icon", // clicking an icon won't initiate dragging
            revert: "invalid", // when not dropped, the item will revert back to its initial position
            helper: "clone",
        });

        $imagesto.droppable({
            accept: "#possible_diagrams > li",
            activeClass: "ui-state-highlight",
            drop: function(event, ui){
                selectImage(ui.draggable);
            }
        });

        $imagesfrom.droppable({
            accept: "#selected_diagrams li",
            activeClass: "ui-state-highlight",
            drop: function(event, ui) {
                unselectImage(ui.draggable);
            }
        });
	*/
        var unselect_icon = "<a href='#' title='Unselect this image' class='ui-icon ui-icon-closethick'>Unselect</a>";
        var selectImage = function( $item ) {
            $item.fadeOut(function() {
                var thumbnails = [];
                /*
                   var $list = $( "ul", $imagesto ).length ?
                   $( "ul", $imagesto ) :
                   $( "<ul class='gallery ui-helper-reset'/>" ).appendTo( $imagesto );
                   */
                var $list = $( "ul", $imagesto );
		//===== begin of comment here because MCQ not required to select Image like Structure question.
                //$item.find( "a.ui-icon-check" ).remove();
                //$item.append( unselect_icon ).appendTo( $list ).fadeIn();
		//===== End of comment here because MCQ not required to select Image like Structure question.
                
            });
        };
	
        // image recycle function
        var check_icon = "<a href='#' title='Select this image' class='ui-icon ui-icon-check'>Select image</a>";
        var unselectImage = function( $item ) {
            $item.fadeOut(function() {
                $item
                .find( "a.ui-icon-closethick" )
                .remove()
                .end()
                .css( "width", "96px")
                .append( check_icon )
                .find( "img" )
                .css( "height", "72px" )
                .end()
                .appendTo( $imagesfrom )
                .fadeIn();
            });
        };

        var viewLargerImage = function( $link ) {
            var src = $link.attr( "tmpadd" ),
                title = $link.siblings( "img" ).attr( "alt" ),
                $modal = $( "img[tmptest$='xx']" );

	console.log('src:', src);
	console.log('title:', title);
	console.log('$modal:', $modal.length);

            if ( $modal.length ) {
		try {

			$modal.dialog("open");
		}
		catch(err) {
			console.log('err message: ' , err.message); 
		}
            } else {
		console.log('no modal going to create img, src is ', src);
                var img = $( "<img tmptest='xx' alt='" + title + "' width='768' height='576' class='invisibleModal' style='display: none; padding: 8px;' />" )
                    .attr( "src", src ).appendTo( "body" );
		console.log('img is , ' , img);
                setTimeout(function() {
	             console.log('dialog going to call');
                    img.dialog({
                        title: title,
                        width: 960,
                        modal: true
                    });
                }, 1 );
            }
        };
	$(".specialpicture").find("li").click(function(event){
	    var $item = $(this);
	    var $imgItem = $item.find('img').attr('src');
	    var $target = $(event.target);
		console.log('is zoomin lo 2 ', $item );
		console.log('is zoomin lo 2 imgItem', $imgItem );
	    if ($target.is("a.ui-icon-zoomin")){
		console.log('is zoomin lo', event.target);
		console.log('target:', $target);
		$target.attr('tmpadd',$imgItem);
		viewLargerImage($target);
	    }else if ($target.is("a.ui-icon-closethick")){
		deleteImage($item);
	    }
	    return false;
	});
        // resolve the icons behavior with event delegation
         
    } 


    var gotosummarize = function(paperid, passed){
	console.log('gotosummarize');
        if (passed){
            timeused = $('#time_show').text().split('/')[0];
            clearInterval(timeoutTimer);
            url = "/student/summarize/?paperid=" + paperid + "&time=" + timeused;
        }else{
            clearInterval(timeoutTimer);
            url = "/student/summarize/?paperid=" + paperid + "&passed=0";
        }
        window.location.href = url;
    };


    function refreshtimeout(){
	var paperid  = intemass.util.getUrl('paperid');
        $.post("/student/checktime/",
        {
            'paperid': paperid,
            'csrfmiddlewaretoken': csrfvalue
        },
        function(payload) {
            if(payload['timeout'] === "yes"){
                var process = $("#question_process_show").text().split('/');
                var index = Number(process[0]);
                var total = Number(process[1]);
                submitpaper(qids[index], paperid);
            }else if (payload){
                $("#time_show").text(payload['timeleft'] + '/' + payload['totaltime']);
            }
        }, 'json');
    };

    refreshtimeout();

})(jQuery);

