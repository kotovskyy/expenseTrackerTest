function confirmDelete(transaction_id) {

    var confirmDelete = confirm("Are you sure you want to delete this transaction?\nThis transaction cannot be restored.");
    if (confirmDelete) {
        var form = document.getElementById("deleteForm_" + transaction_id);
        form.submit();   
    }
}
