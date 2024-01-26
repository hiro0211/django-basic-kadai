window.addEventListener('DOMContentLoaded', function() {
  var faculty = document.querySelector('#id_faculty');
  var department = document.querySelector('#id_department');

  faculty.addEventListener('change', function() {
    var facultyValue = faculty.value;

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/get_department_choices/?faculty=' + encodeURIComponent(facultyValue));
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4 && xhr.status === 200) {
        department.innerHTML = xhr.responseText;
      }
    };
    xhr.send();
  });
});