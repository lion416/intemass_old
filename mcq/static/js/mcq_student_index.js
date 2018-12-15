;(function($, undef) {
    $(function() {

        oTable0 = $('#assignments').dataTable({
                    "bJQueryUI": true,
                    "bProcessing": false,
                    "sAjaxSource": "/mcq/student/getassignedassignments/"
                    });

        oTable1 = $('#selectiveassignments').dataTable({
                    "bJQueryUI": true,
                    "bProcessing": false,
                    "sAjaxSource": "/mcq/student/getretakepapers/"
                    });

        if ($("#dialog-warning p").length > 0){
            var dialogue = $("#dialog-warning").dialog({
                resizable: false,
                width:300,
                modal: true,
                buttons: {
                    OK: function() {
                        $(this).dialog("close");
                    }
                }});
        }
    });
})(jQuery);
