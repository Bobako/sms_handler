function messages_live_search(obj) {
    let header = $("thead");
    let date = $(header).find("#date_search").val();
    let phone = $(header).find("#phone_search").val();
    let text = $(header).find("#text_search").val();
    let prim_status = $(header).find("#prim_status_search").val();
    let sec_status = $(header).find("#sec_status_search").val();
    let text_not_null = $(header).find("#text_not_null_search").is(":checked");
    //console.log(date, phone, text, prim_status, sec_status);
    //console.log(text_not_null.is(":checked"));

    let req = new XMLHttpRequest();
    req.open("GET",
        "api/search/message?date=" + date + "&phone=" + phone + "&text=" + text + "&prim_status="
        + prim_status + "&sec_status=" + sec_status + "&text_not_null="+text_not_null,
        false);
    req.send(null);
    $("tbody").empty();
    $("tbody").append(req.responseText);
}

function subs_live_search(obj) {
    let header = $("thead")
    let name = $(header).find("#name_search").val();
    let phone = $(header).find("#phone_search").val();
    let date = $(header).find("#date_search").val();
    let name_not_null = $(header).find("#name_not_null_search").is(":checked");

    let req = new XMLHttpRequest();
    req.open("GET",
        "api/search/sub?date=" + date + "&phone=" + phone + "&name=" + name + "&name_not_null=" + name_not_null,
        false);
    req.send(null);
    $("tbody").empty();
    $("tbody").append(req.responseText);


}