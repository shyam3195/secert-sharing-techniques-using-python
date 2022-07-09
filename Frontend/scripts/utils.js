function getLocaStorageArray(data) {
    if (data.length > 0) {
        if (data.indexOf(",") === -1) return [data]
        else return data.split(",")
    } else []
    return []
}


function setLocalStorage(data) {
    connections = data['connections']
    data = data['data']
    const user_connections = []
    const user_requested_connections = []
    const user_connection_requested = []
    if (connections.length > 0) {
        for (i = 0; i < connections.length; i++) {
            if (connections[i]['user_id'] === data['user_id'] && connections[i]['is_connected'] === true) {
                user_connections.push(connections[i]['connecting_user_id'])
            }
            if (connections[i]['user_id'] === data['user_id'] && connections[i]['is_requested'] === true) {
                user_requested_connections.push(connections[i]['connecting_user_id'])
            }
            if (connections[i]['connecting_user_id'] === data['user_id'] && connections[i]['is_connected'] === true) {
                user_connections.push(connections[i]['user_id'])
            }
            if (connections[i]['connecting_user_id'] === data['user_id'] && connections[i]['is_requested'] === true) {
                user_connection_requested.push(connections[i]['user_id'])
            }
        }
    }
    localStorage.setItem("username", data['username'])
    localStorage.setItem("email", data['email'])
    localStorage.setItem("is_logged_in", data['is_logged_in'])
    localStorage.setItem("user_id", data['user_id'])
    localStorage.setItem("user_connections", user_connections)
    localStorage.setItem("user_requested_connections", user_requested_connections)
    localStorage.setItem("user_connection_requested", user_connection_requested)
}


function getAllusers() {
    fetch("http://127.0.0.1:5000/users", {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            data = data['data']
            system_users = data
            const current_user_connections = getLocaStorageArray(localStorage.getItem('user_connections'))
            const current_user_requested_connections = getLocaStorageArray(localStorage.getItem('user_requested_connections'))
            const current_user_connections_requested = getLocaStorageArray(localStorage.getItem('user_connection_requested'))
            for (i = 0; i < data.length; i++) {
                if (current_user_connections.length > 0) {
                    for (j = 0; j < current_user_connections.length; j++) {
                        if (current_user_connections[j] === data[i]['_id']['$oid']) {
                            var connection_pub_key = ""
                            let connectionFilter = connections.filter(con => con['user_id'] === data[i]['_id']['$oid'])
                            if (connectionFilter.length > 0) {
                                user_public_key = connectionFilter[0]['user2_pub_key']
                                connection_pub_key = "Your Public Key: " + connectionFilter[0]['user2_pub_key'].toString() + ", Receipient Public Key: " + connectionFilter[0]['user1_public_key'].toString()
                            }
                            let connectionFilter2 = connections.filter(con => con['connecting_user_id'] === data[i]['_id']['$oid'])
                            if (connectionFilter2.length > 0) {
                                user_public_key = connectionFilter2[0]['user1_public_key']
                                connection_pub_key = "Your Public Key: " + connectionFilter2[0]['user1_public_key'].toString() + ", Receipient Public Key: " + connectionFilter2[0]['user2_pub_key'].toString()
                            }

                            current_user_connect.push([data[i]['username'], current_user_connections[j], connection_pub_key])
                        }
                    }
                }
                if (current_user_requested_connections.length > 0) {
                    for (s = 0; s < current_user_requested_connections.length; s++) {
                        if (current_user_requested_connections[s] === data[i]['_id']['$oid']) {
                            current_user_req_connections.push([data[i]['username'], current_user_requested_connections[s]])
                        }
                    }
                }

                if (current_user_connections_requested.length > 0) {
                    for (m = 0; m < current_user_connections_requested.length; m++) {
                        if (current_user_connections_requested[m] === data[i]['_id']['$oid']) {
                            current_user_yet_to_accept.push([data[i]['username'], current_user_connections_requested[m]])
                        }
                    }
                }

                if (data[i]['_id']['$oid'] !== user_id && current_user_connections.indexOf(data[i]['_id']['$oid']) === -1) {
                    $('#users').append(`<option id="${data[i]['_id']['$oid']}" value="${data[i]['username']}">${data[i]['username']}</option>`);
                }
                if (data[i]['_id']['$oid'] !== user_id) {
                    $('#users_encrypt').append(`<option id="${data[i]['_id']['$oid']}" value="${data[i]['username']}">${data[i]['username']}</option>`);
                }
            }

            if (current_user_connect.length > 0) {
                for (k = 0; k < current_user_connect.length; k++) {
                    $('.connections').append(`${current_user_connect[k][0]} ${current_user_connect[k][2] ? "- " + current_user_connect[k][2] : ""}`)
                }
            } else {
                $('.connections').append(`No Connections Yet`)
            }

            if (current_user_req_connections.length > 0) {
                for (l = 0; l < current_user_req_connections.length; l++) {
                    $('.waiting_connections').append(`
                ${current_user_req_connections[l][0]}`)
                }
            } else {
                $('.waiting_connections').append(`No Waiting Connections`)
            }


            if (current_user_yet_to_accept.length > 0) {
                for (n = 0; n < current_user_yet_to_accept.length; n++) {
                    $('.accept_connections').append(`
                ${current_user_yet_to_accept[n][0]}
                <a class="btn btn-info accept_connect_but" id=${current_user_yet_to_accept[n][1]}>Accept</a>`)
                }
            } else {
                $('.accept_connections').append(`No Connections to accept`)
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}


function getCurrentUser() {
    const user_id = localStorage.getItem("user_id")
    const email_id = localStorage.getItem("email")
    localStorage.setItem('user_connections', null)
    localStorage.setItem('user_requested_connections', null)
    localStorage.setItem('user_connection_requested', null)
    fetch("http://127.0.0.1:5000/user", {
            method: 'POST',
            body: JSON.stringify({
                "user_id": user_id,
                "email": email_id,
            }),
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(response => response.json())
        .then(data => {
            setLocalStorage(data)
            getAllusers()
        })
        .catch(err => console.log("error"))
}