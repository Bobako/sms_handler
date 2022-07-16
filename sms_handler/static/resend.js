function resend(message_id){
    let req = new XMLHttpRequest();
    req.open("GET",
        "api/resend?mid="+message_id,
        false);
    req.send(null);
    alert(req.responseText);
}