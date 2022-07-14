$(document).ready(function () {

    var hidden;

    if ($('body').width() > 1510) {
        $(".nav_button").removeClass("hiden_nav_button");
        $("nav div").removeClass("hidden_nav_div");
        hidden = false;
    } else {
        hidden = true;
    }

    $(".nav_button").click(function () {
        if (hidden) {
            $(".nav_button").removeClass("hiden_nav_button");
            $("nav div").removeClass("hidden_nav_div");
            hidden = false;
        } else {
            $(".nav_button").addClass("hiden_nav_button");
            $("nav div").addClass("hidden_nav_div");
            hidden = true;
        }
    });


    $("#new_el_button").click(function () {
        $(".template").clone().toggleClass("template db_el").appendTo("#new_el_div");

    });
});