$(document).ready(function () {
  const ctx1 = document.getElementById("numChart").getContext("2d");
  const ctx2 = document.getElementById("tempChart").getContext("2d");
  const ctx3 = document.getElementById("humidChart").getContext("2d");
  const numChart = new Chart(ctx1, {
    type: "line",
    data: {
      datasets: [{ label: "Number Value" }],
    },
    options: {
      borderWidth: 3,
      borderColor: ["rgba(255, 99, 132, 1)"],
    },
  });
  const tempChart = new Chart(ctx2, {
    type: "line",
    data: {
      datasets: [{ label: "Temperature Value" }],
    },
    options: {
      borderWidth: 3,
      borderColor: ["rgba(245, 229, 22, 1)"],
    },
  });
  const humidChart = new Chart(ctx3, {
    type: "line",
    data: {
      datasets: [{ label: "Humidity Value" }],
    },
    options: {
      borderWidth: 3,
      borderColor: ["rgba(39, 109, 245, 0.8)"],
    },
  });
  var chart_mode = 1;
  myChart = numChart;
  document.getElementById('tempChart').style.display = "none";
  document.getElementById('humidChart').style.display = "none";
  document.getElementById('numChart').style.display = "block";
  var lasttime = Date.now();
  function addData(label, data, updatenumChart) {
    if (myChart != numChart){
      if (myChart.data.labels.length == 0){
        var newlabel = label.slice(0,-3);
        myChart.data.labels.push(newlabel);
        myChart.data.datasets.forEach((dataset) => {
          dataset.data.push(data);
        });
        myChart.update();
      }
      else{
          var lastIndex = myChart.data.labels.length - 1;
          var lastlabel = myChart.data.labels[lastIndex];
          var newlabel = label.slice(0,-3);
          if (lastlabel !== newlabel){
            myChart.data.labels.push(newlabel);
            myChart.data.datasets.forEach((dataset) => {
              dataset.data.push(data);
            });
          myChart.update();
          }
        }
    }
    else{
      var updateChart = parseInt(updatenumChart);
      if (updateChart == 1){
        myChart.data.labels.push(label);
        myChart.data.datasets.forEach((dataset) => {
          dataset.data.push(data);
        });
        myChart.update();
      }
    }
  }
  function removeFirstData() {
    if (myChart.data.labels.length > MAX_DATA_COUNT){
      myChart.data.labels.splice(0, 1);
      myChart.data.datasets.forEach((dataset) => {
      dataset.data.shift();
    })
    }
  }
  const MAX_DATA_COUNT = 25;
  //connect to the socket server.
  //   var socket = io.connect("http://" + document.domain + ":" + location.port);
  var socket = io.connect();
  var max_v = 0;
  var min_v = 0;
  var max_time = "";
  var min_time = "";
  var first_run = true;
  function sendMode(data) {
    $.ajax({
      url: "/predict_mode",
      type: "POST",
      data: { data: data },
    });
  }
  function sendSpeed(data) {
    $.ajax({
      url: "/run_speed",
      type: "POST",
      data: { data: data },
    });
  }
  var output = document.getElementById("currentSpeed");
  var button = document.getElementById("applyButton");
  var inputSpeed = document.getElementById("speedInput");
  button.addEventListener("click", function(){
    var val = inputSpeed.value;
    if (val < 0 || val > 99 || val.toString().length > 3) {
      alert("Invalid speed value!")
    }
    else{
      sendSpeed(val);
    }
  });
  inputSpeed.addEventListener("keypress", function(event){
    if (event.key === 'Enter'){
      $('#applyButton').click();
    }
  });
  
  //receive details from server
  socket.on("updateData", function (msg) {
    output.innerHTML = "Current speed: " + msg.speed.toString();
    if (msg.mode == 2) {
      $("#lcd-mode").removeClass("active");
      $("#led-mode").addClass("active");
    } else {
      $("#led-mode").removeClass("active");
      $("#lcd-mode").addClass("active");
    }

    temp = msg.value;
    msg.value = parseInt(temp);
    if (temp != "" && msg.updatenumChart == 1) {
      if (first_run) {
        min_v = msg.value;
        max_time = msg.time;
        min_time = msg.time;
        max_v = msg.value;
        first_run = false;
      } else {
        if (min_v > msg.value) {
          min_v = msg.value;
          min_time = msg.time;
        }
        if (max_v < msg.value) {
          max_v = msg.value;
          max_time = msg.time;
        }
      }
      $("#max-value").text("Max Value: " + max_v + " (" + max_time + ")");
      $("#min-value").text("Min Value: " + min_v + " (" + min_time + ")");
    }
    $("#date").text("Date: " + msg.date);
    $("#time").text(msg.time);
    $("#value").text(msg.value);
    $("#temper").text(msg.temp);
    $("#humid").text(msg.humid);
    for (let i = 1; i < 4; i++){
      if (i==1){
        myChart = numChart;
        removeFirstData();
        addData(msg.time, msg.value, msg.updatenumChart);
      }
      else{
        if (i==2){
          myChart = tempChart;
          removeFirstData();
          addData(msg.time, msg.temp, msg.updatenumChart);
        }
        else{
          myChart = humidChart;
          removeFirstData();
          addData(msg.time, msg.humid, msg.updatenumChart);
        }
      }
    }
});

  $(".predict-mode ul li a").on("click", function () {
    $(".predict-mode ul li a").removeClass("active");
    $(this).addClass("active");
    data = $(this).data("value");
    sendMode(data);
  });
  $(".chart-mode ul li a").on("click", function () {
    $(".chart-mode ul li a").removeClass("active");
    $(this).addClass("active");
    chart_mode = $(this).data("value");
    if (chart_mode == 1){
      document.getElementById('tempChart').style.display = "none";
      document.getElementById('humidChart').style.display = "none";
      document.getElementById('numChart').style.display = "block";
    }
    else{
      if (chart_mode == 2){
        document.getElementById('humidChart').style.display = "none";
        document.getElementById('numChart').style.display = "none";
        document.getElementById('tempChart').style.display = "block";
      }
      else{
        document.getElementById('tempChart').style.display = "none";
        document.getElementById('numChart').style.display = "none";
        document.getElementById('humidChart').style.display = "block";
      }
    }
  });
});
