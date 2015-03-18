$(document).ready(function() {
    $('#main').DataTable({
        "order": [[ 4, "desc" ]],
        "iDisplayLength": 50,
        "columnDefs": [
            { "orderable": false, "searchable": false, "targets": [0] },
            { "searchable": true, "width": "150px", "targets": [1] },
            { "searchable": true, "targets": [2] },
            { "searchable": false, "targets": [3] },
            { "searchable": false, "targets": [4] },
            { "searchable": false, "targets": [5] },
            { "orderable": false, "searchable": true, "targets": [6] },
            { "type": "date-uk", "searchable": false, "targets": [7] },
            { "orderable": false, "searchable": false, "targets": [8] },
            { "orderable": false, "searchable": false, "targets": [9] },
            {  "searchable": false, "visible": false,  "targets": [10] }
        ],
        initComplete: function () {
            var api = this.api();
            var column = api.column( 6 );
            var select = $('<select><option value=""></option></select>')
                .appendTo( $(column.header()) )
                .on( 'change', function () {
                    var val = $.fn.dataTable.util.escapeRegex($(this).val());
                    column
                        .search(  val , true, false, true )
                        .draw();    
                });
            var genreList = [];    
            column.data().unique().each( 
                    function ( d, j ) {
                        d.split(',').forEach(
                            function (e) {
                                if ($.inArray(e.trim(),genreList) == -1 && e != 'N/A' ){
                                    genreList.push(e.trim());
                                }
                            }
                        )
                    });
            genreList.sort();
            genreList.forEach(
                function (e) {
                    select.append( '<option value="'+e+'">'+e+'</option>' )
                }
            ) 
        }
    });
    $('.fancybox').fancybox({			
        padding: 5,

        openEffect : 'elastic',
        openSpeed  : 150,

        closeEffect : 'elastic',
        closeSpeed  : 150,});
} );