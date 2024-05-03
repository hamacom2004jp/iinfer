cell_chop = (val) => {
    if(val && val.length > 150){
        return `${val.substring(0, 150)}...`;
    }
    return val;
}
// 実行結果をモーダルダイアログに表示
view_result_func = (title, result) => {
    if (!result | Array.isArray(result) && result.length<=0) return;
    let result_modal = $('#result_modal');
    result_modal.find('.modal-title').text(title);
    result_modal.find('.modal-body').html('');
    mk_table_func = () => {
        let table = $('<table class="table table-bordered table-hover table-sm"></table>');
        let table_head = $('<thead class="table-dark bg-dark"></thead>');
        let table_body = $('<tbody></tbody>');
        table.append(table_head);
        table.append(table_body);
        return table;
    }
    let table = mk_table_func();
    result_modal.find('.modal-body').append(table);
    // list型の結果をテーブルに変換
    list2table = (data, table_head, table_body) => {
        Object.keys(data).forEach(i => {
            let row = data[i];
            if(row['success'] && typeof row['success'] == "object" && !Array.isArray(row['success'])){
                dict2table(row['success'], i==0?table_head:null, table_body, row['output_image']);
                return;
            }
            if(typeof row == 'string' || row instanceof String){
                let tr = $('<tr></tr>');
                table_body.append(tr);
                tr.append($(`<td>${row}</td>`));
                return;
            }
            if(Array.isArray(row) && row.length > 0 && typeof row[0] != "object"){
                let tr = $('<tr></tr>');
                table_body.append(tr);
                val = cell_chop(JSON.stringify(row));
                tr.append($(`<td>${row}</td>`));
                return;
            }
            let tr = $('<tr></tr>');
            table_body.append(tr);
            Object.keys(row).forEach(key => {
                let val = row[key];
                if(i==0) {
                    table_head.append($(`<th scope="col" style="word-break:normal">${key}</th>`));
                }
                if(val && val['success'] && Array.isArray(val['success'])){
                    let tbl = mk_table_func()
                    let td = $('<td></td>');
                    td.append(tbl);
                    tr.append(td);
                    list2table(val['success'], tbl.find('thead'), tbl.find('tbody'));
                }
                else if(val && val['success'] && typeof val['success'] == "object"){
                    let tbl = mk_table_func()
                    let td = $('<td></td>');
                    td.append(tbl);
                    tr.append(td);
                    dict2table(val['success'], tbl.find('thead'), tbl.find('tbody'));
                }
                else if(val && Array.isArray(val) && val.length > 0 && typeof val[0] == "object"){
                    let tbl = mk_table_func()
                    let td = $('<td></td>');
                    td.append(tbl);
                    tr.append(td);
                    list2table(val, tbl.find('thead'), tbl.find('tbody'));
                }
                else{
                    tr.append($(`<td>${val}</td>`));
                }
            });
        });
    }
    // dict型の結果をテーブルに変換
    dict2table = (data, table_head, table_body, output_image) => {
        let tr = $('<tr></tr>');
        if(output_image){
            if(table_head)table_head.append($('<th scope="col" style="word-break:normal">output_image</th>'));
            let img = $('<img class="img-thumbnail">').attr('src', `data:image/png;base64,${output_image}`);
            img.css('width','100px').css('height','auto');
            let anchor = $(`<a href="data:image/jpeg;base64,${output_image}" data-lightbox="output_image"></a>`).append(img);
            tr.append($('<td></td>').append(anchor));
        }
        table_body.append(tr);
        Object.keys(data).forEach(key => {
            let val = data[key];
            if(table_head)table_head.append($(`<th scope="col" style="word-break:normal">${key}</th>`));
            if (key != 'warn' && val) {
                if(Array.isArray(val)){
                    if(val.length > 0 && typeof val[0] == "object"){
                        let tbl = mk_table_func()
                        let td = $('<td></td>');
                        td.append(tbl);
                        list2table(val, tbl.find('thead'), tbl.find('tbody'));
                        val = td.html();
                    } else {
                        val = cell_chop(JSON.stringify(val));
                    }
                }
                else if (typeof val == "object") {
                    let tbl = mk_table_func()
                    let td = $('<td></td>');
                    td.append(tbl);
                    dict2table(val, tbl.find('thead'), tbl.find('tbody'));
                    val = td.html();
                }
                else if ((typeof val === 'string' || val instanceof String) && val.length > 150) {
                    val = cell_chop(val);
                }
            }
            tr.append($(`<td style="overflow-wrap:break-word;word-break:break-all;">${val}</td>`));
        });
    }
    let table_head = table.find('thead')
    let table_body = table.find('tbody')
    // 結果をテーブルに変換
    if(result['success'] && Array.isArray(result['success'])){
        list2table(result['success'], table_head, table_body);
    }
    else if(result['success'] && typeof result['success'] == "object"){
        dict2table(result['success'], table_head, table_body, result['output_image']);
    }
    else if(Array.isArray(result)){
        list2table(result, table_head, table_body);
    }
    else if(typeof result === "string" || result instanceof String){
        $('#result_modal').find('.modal-body').html(result);
    }
    else {
        dict2table(result, table_head, table_body);
    }
    result_modal.modal('show');
}
