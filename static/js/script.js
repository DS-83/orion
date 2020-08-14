var i = 0;
function move() {
  if (i == 0) {
    i = 1;
    var elem = document.getElementById("pBar");
    elem.style.display = "block";
    var width = 10;
    var id = setInterval(frame, 10);
    document.getElementById("sync-button").disabled = true;
    function frame() {
      if (width >= 100) {
        clearInterval(id);
        i = 0;
      } else {
        width++;
        elem.style.width = width + "%";
        elem.innerHTML = width + "%";
      }
    }
  }
}
