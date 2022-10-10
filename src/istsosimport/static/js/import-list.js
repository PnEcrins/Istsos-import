$(document).ready(function () {
  var table = $("#import-table").DataTable({
    serverSide: true,
    processing: true,
    ajax: api_imports,
    pageLength: 10,
    columns: [
      { data: "id_import" },
      { data: "procedure.name_prc" },
      { data: "date_import" },
      { data: "file_name" },
      { data: "nb_row_inserted" },
      { data: "nb_row_total" },
      {
        defaultContent:
          ' <button class="delete-btn btn btn-danger"> <i class="bi-trash"></i>  </button> ',
      },
    ],
  });

  $("#import-table tbody").on("click", ".delete-btn", function () {
    var data = table.row($(this).parents("tr")).data();
    // alert(data[0] + "'s salary is: " + data[5]);
    console.log(data);
  });
});
