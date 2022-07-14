function resend(message_id){
    let req = new XMLHttpRequest();
    req.open("GET",
        "/api/resend?mid="+message_id,
        false);
    req.send(null);
    // TODO acquire respond and mark message using #{{message.id}}secondary_service_status
}