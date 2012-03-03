/*
 * Django-CIVIL
 *
 * Running code to allow better handling of fields in change list/form
 */

(function($) {

    var updateUserGroupVisibility = function() {
        var selected = $("#id_action").val();
        if (selected == 0) {
            $("fieldset.module:eq(1)").show();
        }else{
            $("fieldset.module:eq(1)").hide();
        }
    };

    $(document).ready(function(){
        if ($("#changelist-form").length) // exists
        {
            // we are in change_list
        }
        else
        {
            // we are in change_form
            updateUserGroupVisibility();

            $("#id_action").change(function(e) {
                updateUserGroupVisibility();
            });
        }
    });
}(django.jQuery));
