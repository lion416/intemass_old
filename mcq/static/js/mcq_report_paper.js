$(document).ready(function(){
    console.log("mcq report_paper.js document ready")
    var oTable = $('#data_list').dataTable(
        {
            "bJQueryUI": true,
            // OLD: "width":"50px",
            "bProcessing": true,
            "bSeverside": true,
            // "bAutoWidth": false,
            "bAutoWidth": true,
            "sAjaxSource": "/mcq/paper/getall/",

            "fnServerData": function( sSource, aoData, fnCallback ) {
                var oData={"pids": pids};
                //$.post(sSource,oData,function(json) { 
                //    fnCallback(json);
                //},"json");	
		$.ajax({
		  type: "POST",
		  url: sSource,
		  data: oData,
		  dataType: 'json',
		  success: function(msg){
			fnCallback(msg);
			console.log(msg)
		  },
		  error: function(XMLHttpRequest, textStatus, errorThrown) {
		     //alert(XMLHttpRequest.responseText);
		  }
		});



            }
        });
});


function submitform(){
    var oTable = $('#data_list').dataTable();
    var year = $('#id_year').val();
    var subject = $('#id_subject').val();
    var level = $('#id_level').val();
    oTable.fnFilter(year,0);
    oTable.fnFilter(subject,1);
    oTable.fnFilter(level,2);
}

function checkdetailpaper(){
    console.log("in checkdetailpaper")
    var paperids = [];
    var oTable = $('#data_list').dataTable();
    
    $('input', oTable.fnGetNodes()).each(function(){
        if($(this).attr('checked') === 'checked'){
            paperids.push($(this).attr('name'));
		//alert($(this).attr('name'));
        }
    });
    console.log("paperids: " + paperids);
    $('#paperids').val(paperids);
    document.formx1.submit();
}

function selectall(){
    var oTable = $('#data_list').dataTable();
    $('input', oTable.fnGetNodes()).each(function(){
        $(this).attr('checked',!$(this).attr('checked'));
    });
}