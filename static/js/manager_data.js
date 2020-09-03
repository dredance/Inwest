function formatDate(date) {
     var d = new Date(date),
         month = '' + (d.getMonth() + 1),
         day = '' + d.getDate(),
         year = d.getFullYear();

     if (month.length < 2) month = '0' + month;
     if (day.length < 2) day = '0' + day;

     return [year, month, day].join('-');
};


$('input#id_update_form-okres').replaceWith('<select name="update_form-okres" class="form-control"' +
                                            ' id="id_update_form-okres"></select>')


$('#id_update_form-projekt').on("change", function (){
  $.ajax({
    url: `http://gasproject.herokuapp.com/api/okresy/?psp=${$(this).val()}`,
    type: "GET",
    dataType: "json"
  }).done(function(results){
    var selectValues = results[0].okresy
    $('#id_update_form-okres').children().remove()
    $.each(selectValues, function(key, value) {
     $('#id_update_form-okres')
         .append($("<option></option>")
                    .attr("value", value)
                    .text(value));
    });
  });
});


$('#id_insert_form-projekt').on("change", function (){
  $.ajax({
    url: `http://gasproject.herokuapp.com/api/okresy/?psp=${$(this).val()}`,
    type: "GET",
    dataType: "json"
  }).done(function(results){
    if (results[0].okresy) {
      $('#id_insert_form-okres').addClass("disabled")
      $('#id_insert_form-okres').css('background-color','#c1bebe')
      $('#id_insert_form-download_data').attr("checked", "")
      $('#id_insert_form-download_data').parent().show()
      var dateMax = new Date(results[0].okresy[0])
      let okresNew = new Date(dateMax.getFullYear(),dateMax.getMonth()+2,0)
      $('#id_insert_form-okres').val(formatDate(okresNew))
    } else {
      $('#id_insert_form-okres').removeClass("disabled")
      $('#id_insert_form-okres').css('background-color', 'white')
      $('#id_insert_form-download_data').attr("checked", false)
      $('#id_insert_form-download_data').parent().hide()
    }
    });
});

