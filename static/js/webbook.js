jQuery(document).ready(function () {
    var $ = jQuery;

    $(".progress-bar").each(function () {
        var value = $(this).attr("aria-valuenow");

        $(this).css("width", value + "%");
    });

    $(".book-display button[value=continue]").on("click", function (event) {
        // validate form
        var completed = true;

        $(this).closest("form").find("textarea").each(function () {
            if ( $(this).val() == "" && $(this).prop("required") ){
                completed = false;
            }
        });

        if ( !completed ) {
            alert("Enter your response to every question.");
            event.preventDefault();
        }
    });

    // purchase
    $(".store-discounts-buy-wrapper select[name=group]").each(function () {
        var $select = $(this);
        var $name = $select.parent().find("[name=group_name]");

        $select.on("change", refresh);
        refresh();

        function refresh() {
            if ( $select.val() == "new" ) {
                $name.show();
            } else {
                $name.hide();
            }
        };
    });

    // send-message dialog
    (function () {
        var $dialog = $("#send-message-dialog");
        var $form = $dialog.find("form");
        var $alert = $dialog.find(".alert");

        $("a.group-message").on("click", function (event) {
            event.preventDefault();

            var recipient_name = $(this).data("recipientName");
            var user_id = $(this).data("userId");
            var group_id = $(this).data("groupId");

            $dialog.find(".alert").attr("class", "alert").hide();
            $dialog.find(".recipient-name").text(recipient_name);

            if ( user_id ) {
                $dialog.find("input[name=user_id]").val(user_id);
            } else {
                $dialog.find("input[name=user_id]").val("");
            }

            if ( group_id ) {
                $dialog.find("input[name=group_id]").val(group_id);
            } else {
                $dialog.find("input[name=group_id]").val("");
            }

            $dialog.modal("show");
        });

        $dialog.find(".btn-primary").click(function () {
            var data = $form.serialize();
            var url = $form.attr("action");

            show_message("info", "Sending...");

            $.post(url, data, function (resp) {
                if ( resp.error ) {
                    show_message("danger", resp.error);
                } else if ( resp.success ) {
                    show_message("success", resp.success);
                } else {
                    $dialog.modal("hide");
                }
            }, "json").always(function () {
            });
        });

        function show_message(type, text) {
            $alert.attr("class", "alert").addClass("alert-" + type).text(text).show();
        }
    })();

    // claim-code dialog
    (function () {
        var $dialog = $("#claim-code-dialog");
        var $form = $dialog.find("form");
        var $alert = $dialog.find(".alert");

        $("a.claim-code").on("click", function (event) {
            event.preventDefault();

            var claim_code = $(this).data("claim_code");

            $dialog.find("textarea[name=message]").val("You have received a workbook on Discipleship Workbooks. You can access this workbook by using the following gift code.\n\nGift Code: " + claim_code + "\n\nRedeem at: http://www.discipleshipworkbooks.com/store/redeem/?code=" + claim_code);

            $dialog.find(".alert").attr("class", "alert").hide();
            $dialog.modal("show");
        });

        $dialog.find(".btn-primary").click(function () {
            var data = $form.serialize();
            var url = $form.attr("action");

            show_message("info", "Sending...");

            $.post(url, data, function (resp) {
                if ( resp.error ) {
                    show_message("danger", resp.error);
                } else if ( resp.success ) {
                    show_message("success", resp.success);
                } else {
                    $dialog.modal("hide");
                }
            }, "json").always(function () {
            });
        });

        function show_message(type, text) {
            $alert.attr("class", "alert").addClass("alert-" + type).text(text).show();
        }
    })();

    // youtube
    $('<div id="youtube-modal-wrapper" class="youtube-modal-wrapper"></div>').appendTo("body");
    $(".youtube-link").on("click", function (event) {
        var url = $(this).attr("href");
        url = get_youtube_embed_url(url);

        var $modal = $("#youtube-modal-wrapper");
        $modal.html("");
        var $iframe = $('<iframe frameborder="0"></iframe>').attr("src", url);

        $('<div class="youtube-modal-header">x</div>').appendTo($modal);
        $('<div class="youtube-modal-content"></div>').append($iframe).appendTo($modal);

        $("#youtube-modal-wrapper").fadeIn();
        $("body").addClass("modal-open");

        event.preventDefault();

        function get_youtube_embed_url (url) {
            var id_pos = url.indexOf("v=");

            if ( id_pos > 0 ) {
                return "http://www.youtube.com/embed/" + url.substr(id_pos + 2) + "?autoplay=1&fs=0&playsinline=1";
            }
            return url;
        }
    });
    $("#youtube-modal-wrapper").click(function () {
        $(this).find("iframe").attr("src", "");
        $(this).find(".youtube-modal-content").html("");
        $(this).fadeOut();
        $("body").removeClass("modal-open");
    });
});

function open_appendix(link_name) {
    switch(link_name) {
        case "marriage_appendix_a":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1275/";
            break;
        case "marriage_appendix_b":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1277/";
            break;
        case "marriage_appendix_c":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1281/";
            break;
        case "marriage_appendix_d":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1283/";
            break;
        case "marriage_appendix_e":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1285/";
            break;
        case "marriage_appendix_f":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1290/";
            break;
        case "marriage_appendix_g":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1310/";
            break;
        case "marriage_appendix_h":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1324/";
            break;
        case "marriage_appendix_i":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1368/";
            break;
        case "marriage_appendix_j":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1373/";
            break;
        case "marriage_appendix_k":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1375/";
            break;
        case "marriage_appendix_l":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1429/";
            break;
        case "marriage_appendix_m":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1443/";
            break;
        case "marriage_appendix_n":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1459/";
            break;
        case "marriage_appendix_o":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1480/";
            break;
        case "marriage_appendix_p":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1520/";
            break;
        case "marriage_appendix_q":
            urli = "http://www.discipleshipworkbooks.com/workbook/marriage-workbook/1581/";
            break;
        case "parenting_appendix_a":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1112/";
            break;
        case "parenting_appendix_b":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1120/";
            break;
        case "parenting_appendix_c":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1124/";
            break;
        case "parenting_appendix_d":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1126/";
            break;
        case "parenting_appendix_e":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1130/";
            break;
        case "parenting_appendix_f":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1135/";
            break;
        case "parenting_appendix_g":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1152/";
            break;
        case "parenting_appendix_h":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1155/";
            break;
        case "parenting_appendix_i":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1163/";
            break;
        case "parenting_appendix_j":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1170/";
            break;
        case "parenting_appendix_k":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1175/";
            break;
        case "parenting_appendix_l":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1177/";
            break;
        case "parenting_appendix_m":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1179/";
            break;
        case "parenting_appendix_n":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1186/";
            break;
        case "parenting_appendix_o":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1194/";
            break;
        case "parenting_appendix_p":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1204/";
            break;
        case "parenting_appendix_q":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1206/";
            break;
        case "parenting_appendix_r":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1208/";
            break;
        case "parenting_appendix_s":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1210/";
            break;
        case "parenting_appendix_t":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1260/";
            break;
        case "parenting_appendix_u":
            urli = "http://www.discipleshipworkbooks.com/workbook/parenting-discipleship/1262/";
            break;
    }
    window.open(urli, "foobee", "toolbar=yes, scrollbars=yes, resizable=yes, width=600, height=600");
}
