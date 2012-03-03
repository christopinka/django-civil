(function(){

	CKEDITOR.dialog.add('YoutubeEmbed', function(editor) {
		return {
			title : 'Embed Youtube Video',
			minWidth : 320,
			minHeight : 200,
			onOk: function() {
                var dialog = this, data = {};
                this.commitContent(data);

                var iframe = editor.document.createElement( 'iframe' );
                iframe.setAttribute('type', 'text/html');
                iframe.setAttribute('frameborder', '0');
                iframe.setAttribute('width', data.width);
                iframe.setAttribute('height', data.height);
                iframe.setAttribute('src', 'http://www.youtube.com/embed/' + data.video_code);
                editor.insertElement( iframe );
            },
			contents: [{
                id: 'page1',
                label: 'Youtube',
                title: '',
                accessKey: 'Y',
                elements:[
                  {
                      type : 'text',
                      label : 'Youtube Video Code',
                      id : 'youtubeVideoCodeID',
                      validate : CKEDITOR.dialog.validate.notEmpty( 'There must be a Youtube video code specified.' ),
                      required : true,
                      'default' : '',
                      commit : function( data ) { data.video_code = this.getValue(); }
                  },
                  {
                      type : 'text',
                      label : 'Width',
                      id : 'youtubeVideoWidth',
                      'default' : '600',
                      commit : function( data ) { data.width = this.getValue(); }
                  },
                  {
                      type : 'text',
                      label : 'Height',
                      id : 'youtubeVideoHeight',
                      'default' : '400',
                      commit : function( data ) { data.height = this.getValue(); }
                  }
                ]
            }]
		};
	});

})();
