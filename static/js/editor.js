$(document).ready(function () {
    // Sort Chapters of a Book
    $(".books-headings").each(function () {
        var $ol = $(this);
        var url = $ol.data("sortChaptersUrl");

        if( !url ){
            // sorting is not enabled
            return;
        }

        $ol.sortable({
            items:  "li",
            update: function () {
                setTimeout(submit_sorting, 100);
            }
        });

        function submit_sorting () {
            var data = {
                "items":                [],
                "csrfmiddlewaretoken":  null
            };

            $ol.find("input[name=items]").each(function () {
                data["items"].push( $(this).val() );
            });
            data["csrfmiddlewaretoken"] = $("input[name=csrfmiddlewaretoken]").val();

            $.post(url, data);
        };

    });

    // Sort Items inside a Book
    $(".books-items").each(function () {
        var $ol = $(this);
        var url = $ol.data("sortItemsUrl");


        if( ! url ){
            // sorting is not enabled
            return;
        }

        $ol.sortable({
            items:  "li:not(.h1-item)",
            update: function () {
                setTimeout(submit_sorting, 100);

            }
        });

        function submit_sorting () {
            var data = {
                "items":                [],
                "csrfmiddlewaretoken":  null
            };

            $ol.find("input[name=items]").each(function () {
                data["items"].push( $(this).val() );
            });
            data["csrfmiddlewaretoken"] = $("input[name=csrfmiddlewaretoken]").val();

            $.post(url, data);
        };
    });
});
