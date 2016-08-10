/*
 * Module: jQuery Scroll To Top Plugin
 * Version: 1.0.2
 * Author: Chaikin Evgenii
 * Release date: 26 Oct 2015
 * Updated: 29 Oct 2015
 * Site: http://www.fater.ru
 * Dependencies: jQuery
 * */


(function ($)
{
	// Options
	var opt =
	{
		top_standoff: 700,
		speed: 400,
		segment: true,
		class: 'scroll1',
		object_id: 'jquery-scrolltotop'
	};

	$.scrolltotop = function (options)
	{
		if (options)
		{
			$.extend (opt, options);
		}

		$ ('body').append ('<div id="' + opt.object_id + '" class="' + opt.class + '"></div>');

		$ (window).scroll (function ()
		{
			clearTimeout (opt.scrollTimer);
			opt.scrollTimer = setTimeout (function ()
			{
				if ($ (this).scrollTop () > opt.top_standoff)
				{
					$ ('#' + opt.object_id).fadeIn ();
				}
				else
				{
					$ ('#' + opt.object_id).fadeOut ();
				}
			}, 350);

		});

		$ ('#' + opt.object_id).on ('click', function ()
		{
			if (opt.segment == true)
			{
				var speed = ($ (window).scrollTop () / opt.top_standoff) * opt.speed;
			}
			else
			{
				var speed = opt.speed;
			}
			$ ('body,html').animate ({scrollTop: 0}, speed);
		});
	}
}) (jQuery);