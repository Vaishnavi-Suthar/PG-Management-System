
document.addEventListener("DOMContentLoaded", function () {

    /* ----------------------------
       1️⃣  OPEN EDIT TENANT MODAL
    ----------------------------- */
    document.querySelectorAll(".edit-tenant-btn").forEach(button => {
        button.addEventListener("click", function () {
            const tenantId = this.getAttribute("data-id");

            fetch(`/get_tenant/${tenantId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById("editTenantId").value = data.id;
                    document.getElementById("editName").value = data.name;
                    document.getElementById("editPhone").value = data.phone;
                    document.getElementById("editAadhar").value = data.aadhar;
                    document.getElementById("editAddress").value = data.address;
                    document.getElementById("editJoinDate").value = data.join_date;

                    // Room selector (Single room)
                    document.querySelectorAll(".edit-room-option").forEach(opt => {
                        opt.selected = (opt.value == data.room_id);
                    });

                    new bootstrap.Modal(document.getElementById("editTenantModal")).show();
                })
                .catch(err => console.error("Error loading tenant:", err));
        });
    });


    /* ----------------------------
       2️⃣  OPEN VIEW TENANT MODAL
    ----------------------------- */
    document.querySelectorAll(".view-tenant-btn").forEach(button => {
        button.addEventListener("click", function () {
            const tenantId = this.getAttribute("data-id");

            fetch(`/get_tenant/${tenantId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById("viewName").textContent = data.name;
                    document.getElementById("viewPhone").textContent = data.phone;
                    document.getElementById("viewAadhar").textContent = data.aadhar;
                    document.getElementById("viewAddress").textContent = data.address;
                    document.getElementById("viewJoinDate").textContent = data.join_date;
                    document.getElementById("viewRoom").textContent = data.room_number;

                    new bootstrap.Modal(document.getElementById("viewTenantModal")).show();
                })
                .catch(err => console.error("Error loading details:", err));
        });
    });



    /* ----------------------------
       3️⃣ DELETE TENANT CONFIRM
    ----------------------------- */
    document.querySelectorAll(".delete-tenant-btn").forEach(button => {
        button.addEventListener("click", function () {
            const tenantId = this.getAttribute("data-id");

            if (confirm("Are you sure you want to delete this tenant?")) {
                fetch(`/delete_tenant/${tenantId}`, { method: "POST" })
                    .then(res => res.json())
                    .then(result => {
                        if (result.status === "success") {
                            location.reload();
                        } else {
                            alert("Error deleting tenant!");
                        }
                    });
            }
        });
    });



    /* ----------------------------------------
       4️⃣ SELECT ALL ROOM CHECKBOXES (SAFE)
    ----------------------------------------- */
    const selectAll = document.getElementById("selectAll");
    if (selectAll) {
        selectAll.addEventListener("change", function () {
            const checked = this.checked;
            document.querySelectorAll(".room-checkbox").forEach(cb => {
                cb.checked = checked;
            });
        });
    }

});
