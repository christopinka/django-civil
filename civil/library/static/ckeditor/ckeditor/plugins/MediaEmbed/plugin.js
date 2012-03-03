(function() {

    //Section 2 : Create the button and add the functionality to it

    var pluginName = 'MediaEmbed';
    CKEDITOR.plugins.add(pluginName,
    {
        init: function(editor)
        {
            var functionName = 'YoutubeEmbed';
            CKEDITOR.dialog.add(functionName, this.path + 'dialogs/' + functionName + '.js');
            editor.addCommand(functionName, new CKEDITOR.dialogCommand(functionName));
            editor.ui.addButton(functionName, {
                label: 'Youtube Embed',
                icon: this.path + "icon.gif",
                command: functionName
            });
        }
    });

})();
