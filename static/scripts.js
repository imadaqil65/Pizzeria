let products = [];
let total = 0;
let currentOrder = {};

// menu page add to cart
function add(product) {
    products.push(product); // add product to list
    total = total + parseFloat(product["price"]);
    document.getElementById("total-price").innerHTML = `€${total.toFixed(2)}` // current total
    display_list();
}

// menu page remove from cart
function remove(index) {
    total = total - parseFloat(products[index]["price"]);
    console.log(products.splice(index, 1)); // remove product from list
    document.getElementById("total-price").innerHTML = `€${Math.abs(total.toFixed(2))}` // current total
    display_list();
}

// menu page display list
function display_list() {
    console.log(products)
    xTable = document.getElementsByClassName('order-container')[0];
    xTable.innerHTML = "<caption><p>Your current order</p></caption><tr><th>#</th><th>Item</th><th>Price</th><th>Remove</th></tr>";
    count = 0
    products.forEach(x => {
        tr = document.createElement('tr');
        listIndex = document.createElement('td');
        listItem = document.createElement('td');
        listPrice = document.createElement('td');
        listDelete = document.createElement('td');
        listIndex.innerHTML = count + 1;
        listItem.innerHTML = x["name"];
        listPrice.innerHTML = "€" + x["price"];
        listDelete.innerHTML = "<button class=buttondelete onclick=\"remove(" + count + ")\">X</button>";
        tr.appendChild(listIndex);
        tr.appendChild(listItem);
        tr.appendChild(listPrice);
        tr.appendChild(listDelete);
        xTable.appendChild(tr); 
        count++;
    });
}

// menu page checkout button
function checkout() {
    sessionStorage.currentOrder = JSON.stringify(products)
    window.location.href = "../checkout";
}

// checkout page onload
function checkout_page() {
    products = JSON.parse(sessionStorage.currentOrder)
    estimatePrepareTime = 0
    totalPrice = 0
    document.getElementById("item-count").innerHTML = products.length + " items";
    xTable = document.getElementById("products");
    products.forEach(x => {
        row = document.createElement('p');
        row.innerHTML = ["<a>", x["name"],"</a> <span class=\"price\">€", x["price"], "</span>"].join("");
        console.log(row.innerHTML);
        xTable.appendChild(row);
        estimatePrepareTime += parseFloat(x["cooktime"]);
        totalPrice += parseFloat(x["price"]);
    });
    document.getElementById("checkout-total-price").innerHTML = ["<b>€", totalPrice.toFixed(2), "</b>"].join("");
    // prepare time of all items
    var date = new Date(0);
    date.setSeconds(estimatePrepareTime);
    timeString = date.toISOString().substring(11, 19);
    document.getElementById("checkout-est-time").innerHTML = ["<b>", timeString, "</b>"].join("");
    // how long is the whole order queue
    xmlhttp = new XMLHttpRequest();
    url = "http://127.0.0.1:5000/queue_time"
    xmlhttp.open("GET", url, false);
    xmlhttp.send( null );
    date = new Date(0);
    date.setSeconds(parseFloat(JSON.parse(xmlhttp.responseText)[1]));
    console.log(date)
    timeString = date.toISOString().substring(11, 19);
    document.getElementById("checkout-est-wait").innerHTML = ["<b>", timeString, " (", JSON.parse(xmlhttp.responseText)[0], " orders)</b>"].join("");
}

// checkout page confirm order button
function addOrder() {
    url = "http://127.0.0.1:5000/add_order";
    // 0: products, 1: name, 2: phone, 3: time_preference, 4: message
    order = [products, document.getElementById("name").value, document.getElementById("phone").value, document.getElementById("time").value, document.getElementById("subject").value]
    xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", url, false);
    xmlhttp.setRequestHeader("Content-type", "application/json");
    xmlhttp.send(JSON.stringify(order));
    window.location.href = "../thanks";
}

// kitchen start current order
function startOrder(orderIndex) {
    url = "http://127.0.0.1:5000/current_order";
    postRequest(orderIndex, url);
}

// kitchen finish current order
function finishOrder(orderIndex) {
    url = "http://127.0.0.1:5000/finish_order";
    postRequest(orderIndex  , url);
}

function postRequest(orderIndex, url) {
    xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", url, false);
    xmlhttp.setRequestHeader("Content-type", "application/json");
    xmlhttp.send(orderIndex);
}