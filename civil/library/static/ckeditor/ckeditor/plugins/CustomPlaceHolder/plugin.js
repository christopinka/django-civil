(function() {

    //Section 2 : Create the button and add the functionality to it

    var pluginName = 'CustomPlaceHolder';
    CKEDITOR.plugins.add(pluginName,
    {
        init: function(editor)
        {
            CKEDITOR.dialog.add(pluginName, this.path + 'dialogs/' + pluginName + '.js');
            editor.addCommand(pluginName, new CKEDITOR.dialogCommand(pluginName));
            editor.ui.addButton(pluginName,
                {
                    label: 'Custom Placeholder',
                    icon: this.path + "icon.gif",
                    command: pluginName
                });
        }
    });

})();
