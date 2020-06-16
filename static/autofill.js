function autoDate(button_id) {
  // Now date
  var now = new Date();
  // Switch between clicked buttons
  switch (button_id) {

      // This week
      case "tweek_btn" :
          // Date
          var sun = document.getElementById("date_end");
          var mon = document.getElementById(button_id).value;
          document.getElementById("date_start").value = mon;
          sun.value = mon;
          sun.stepUp(6);
          // Time
          document.getElementById("time_start").value = "00:00:00";
          document.getElementById("time_end").value = "23:59:59";
          break;
      // This day
      case "tday_btn" :
          document.getElementById("date_start").value = now.yyyymmdd();
          document.getElementById("date_end").value = now.yyyymmdd();
          document.getElementById("time_start").value = "00:00:00";
          document.getElementById("time_end").value = "23:59:59";
          break;
      // This hour
      case "thour_btn" :
          document.getElementById("date_start").value = now.yyyymmdd();
          document.getElementById("time_start").value = now.this_h_hhmmss();
          document.getElementById("date_end").value = now.yyyymmdd();
          var timeend = document.getElementById("time_end");
          timeend.value = now.this_h_hhmmss();
          timeend.stepUp(3599);
          break;
      // Previous week
      case "pweek_btn" :
          // Previous Monday
          var pmon = document.getElementById("date_start");
          pmon.value = document.getElementById(button_id).value;
          pmon.stepDown(7);
          // Previous sunday
          var sun = document.getElementById("date_end");
          sun.value = pmon.value;
          sun.stepUp(6);
          // Time
          document.getElementById("time_start").value = "00:00:00";
          document.getElementById("time_end").value = "23:59:59";
          break;
      // Previous day
      case "pday_btn" :
          document.getElementById("date_start").value = now.yyyymmdd();
          document.getElementById("date_start").stepDown();
          document.getElementById("date_end").value = now.yyyymmdd();
          document.getElementById("date_end").stepDown();
          document.getElementById("time_start").value = "00:00:00";
          document.getElementById("time_end").value = "23:59:59";
          break;
      // Previous hour
      case "phour_btn" :
          document.getElementById("date_start").value = now.yyyymmdd();
          document.getElementById("date_end").value = now.yyyymmdd();
          document.getElementById("time_start").value = now.this_h_hhmmss();
          document.getElementById("time_start").stepDown(3600);
          document.getElementById("time_end").value = now.this_h_hhmmss();
          document.getElementById("time_end").stepDown();
          break;

  }
}
// Date prototype yyyy-mm-dd
Date.prototype.yyyymmdd = function() {
  var mm = this.getMonth() + 1; // getMonth() is zero-based
  var dd = this.getDate();

  return [this.getFullYear(),
          (mm>9 ? '' : '0') + mm,
          (dd>9 ? '' : '0') + dd
        ].join('-');
};

// Date prototype this hour hh:mm:ss
Date.prototype.this_h_hhmmss = function() {
  var hh = this.getHours();

  return [(hh>9 ? '' : '0') + hh, '00', '00'].join(':');
};

//Save the value function - save it to localStorage as (ID, VALUE)
function saveValue(e) {
    var id = e.id;  // get the sender's id to save it .
    var val = e.value; // get the value.
    localStorage.setItem(id, val);// Every time user writing something, the localStorage's value will override .
};

//get the saved value function - return the value of "v" from localStorage.
function getSavedValue(v) {
    if (!localStorage.getItem(v)) {
        return "";// Default
    }
    return localStorage.getItem(v);
};
