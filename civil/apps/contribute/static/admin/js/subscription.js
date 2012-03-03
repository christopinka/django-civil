/*
 * Django-CIVIL
 *
 * Running code to allow better handling of fields in change list/form
 */

(function($) {

    var updateContributionVisibility = function() {
        var checkbox = $("#id_has_contribution");
        if (checkbox.is(":checked")) {
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
            updateContributionVisibility();

            $("#id_has_contribution").click(function(e) {
                updateContributionVisibility();
            });
        }
    });
    
}(django.jQuery));
