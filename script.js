setInterval(()=>{
fetch('/status')
.then(res=>res.json())
.then(data=>{
document.getElementById("cpu").innerText = "CPU: " + data.cpu + "%";
document.getElementById("ram").innerText = "RAM: " + data.ram + "%";
});
},2000);