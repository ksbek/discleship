
$(document).ready(function(){
	// sort chapters of a book
	$('.editor-book-wrapper .books-headings').each(function(){
		var $ol = $(this);
		var url = $ol.data('sortChaptersUrl');

		if( ! url ){
			// sorting is not enabled
			return;
		}

		$ol.sortable({
			items: "li",
			update: function(){
				setTimeout(submit_sorting, 100);

			}
		});
		function submit_sorting(){
			var data = { 'items': [], 'csrfmiddlewaretoken': null };

			$ol.find('input[name=items]').each(function(){
				data['items'].push( $(this).val() );
			});
			data['csrfmiddlewaretoken'] = $('input[name=csrfmiddlewaretoken]').val();

			$.post(url, data);
		};

	});

	// sort items inside a book
	$('.editor-chapter-wrapper .books-items').each(function(){
		var $ol = $(this);
		var url = $ol.data('sortItemsUrl');


		if( ! url ){
			// sorting is not enabled
			return;
		}

		$ol.sortable({
			items: "li:not(.h1-item)",
			update: function(){
				setTimeout(submit_sorting, 100);

			}
		});
		function submit_sorting(){
			var data = { 'items': [], 'csrfmiddlewaretoken': null };

			$ol.find('input[name=items]').each(function(){
				data['items'].push( $(this).val() );
			});
			data['csrfmiddlewaretoken'] = $('input[name=csrfmiddlewaretoken]').val();

			$.post(url, data);
		};
	});
});
