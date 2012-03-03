(function(){

	CKEDITOR.dialog.add('CustomPlaceHolder', function(editor) {
		return {
			title : 'Custom Place Holders',
			minWidth : 320,
			minHeight : 400,
            //buttons:[{
            //    type:'button',
            //    id:'insertID', /* note: this is not the CSS ID attribute! */
            //    label: 'Insert',
            //    onClick: function() {
            //       //action on clicking the button
            //    }
            //}, CKEDITOR.dialog.okButton, CKEDITOR.dialog.cancelButton],
			//onOk: function() {},
			//onLoad: function() {},
			//onShow: function() {
            //    var elem = this.getParentEditor().getSelection().getSelectedElement(); //get the current selected element
            //    this.setupContent(elem); //this function will call all the setup function for all uiElements
            //},
			//onHide: function() {},
			//onCancel: function() {},
			contents: [{
                id: 'page1',
                label: 'Contact',
                title: 'Contact Title',
                accessKey: 'P',
                elements:[
                  {
                      type : 'text',
                      label : 'Test Text 1',
                      id : 'testText1',
                      'default' : 'hello world!'
                  }
                ]
            }]
		};
	});

})();
