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

// User edit set values
function userEdit(id) {
    // Get row by id
    var data = document.getElementById("usersTable").rows.namedItem(id);
    // Loop for elements from 0 to 4
    var l = 5;
    var i;
    for (i = 0; i < l; i++) {
        var r = document.getElementById("collapseRow1").children[i].children[0];
        r.value = data.children[i].textContent;
    }
    // Element 5
    r = document.getElementById("collapseRow2").children[0].children[0].children[1];
    r.value = data.children[5].textContent;
    // Element 6
    r = document.getElementById("collapseRow2").children[1].children[0].children[1];
    r.value = data.children[6].textContent;

    // Fill hidden id
    document.getElementById('hidden_id').value = id;
};

// Save reports
function saveReport() {
    var table = document.getElementById("personTable")
    var mtable = document.getElementById("modalTable")
    // Clear table
    for (var i = 0, row; row = mtable.rows[i]; i++) {
      mtable.deleteRow(i);
    }
    // Iterate each row in table
    for (var i = 1, row; row = table.rows[i]; i++) {
        if (row.cells[0].children[0].children[0].checked === true) {
          let clone = row.cloneNode(true);
          mtable.appendChild(clone);
        }
    }
};

// Fill hidden_id
function fillHidden(id) {
    document.getElementById('hidden_id').value = id;
};

// Display div
function displayDiv(id) {
    let date = document.getElementById('date');
    let time = document.getElementById('time');
    let weekday = document.getElementById('weekday');
    let period = document.getElementById(id)
    if (period.value == 'weekly' || period.value == 'daily') {
        weekday.style.display = 'block';
        time.style.display = 'block';
    };
    if (period.value == 'monthly') {
        date.style.display = 'block';
    };
}
