import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="Enterprise Stock Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 0. ระบบพจนานุกรมภาษา (Language Dictionary: TH / EN)
# ----------------------------------------------------
LANG = {
    "th": {
        "title": "ระบบจัดการสต็อกสินค้าและคลังสินค้า",
        "sidebar_lang": "🌐 เลือกภาษา / Language",
        "sidebar_user": "👤 ผู้ใช้งานปัจจุบัน",
        "role_label": "สิทธิ์:",
        "branch_label": "สาขา:",
        "menu": "📌 เมนูหลัก",
        "m_dashboard": "📊 แดชบอร์ดภาพรวม",
        "m_inventory": "📦 จัดการรายการสินค้า",
        "m_import": "📥 นำเข้าสินค้า",
        "m_export": "📤 เบิกออกสินค้า",
        "m_history": "📜 ประวัติการทำรายการ",
        "m_pr_po": "📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)",
        "m_admin": "⚙️ จัดการแอดมินและสิทธิ์",
    },
    "en": {
        "title": "Enterprise Stock & Warehouse Management System",
        "sidebar_lang": "🌐 Select Language / ภาษา",
        "sidebar_user": "👤 Current User",
        "role_label": "Role:",
        "branch_label": "Branch:",
        "menu": "📌 Main Menu",
        "m_dashboard": "📊 Dashboard",
        "m_inventory": "📦 Inventory Master",
        "m_import": "📥 Stock In",
        "m_export": "📤 Stock Out",
        "m_history": "📜 Transaction History",
        "m_pr_po": "📝 Purchase Request (PR) & PO",
        "m_admin": "⚙️ Admin & Permissions",
    }
}

# ----------------------------------------------------
# 1. จัดการ Session State (ฐานข้อมูลจำลองในหน่วยความจำ)
# ----------------------------------------------------
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'th'

if 'inventory' not in st.session_state:
    st.session_state['inventory'] = pd.DataFrame([
        {"SKU": "ITEM-001", "Name": "Laptop Pro 15", "Category": "Electronics", "Branch": "Headquarter", "Price": 35000, "Qty": 15, "Min_Qty": 5},
        {"SKU": "ITEM-002", "Name": "Wireless Mouse", "Category": "Accessories", "Branch": "Headquarter", "Price": 750, "Qty": 50, "Min_Qty": 10},
        {"SKU": "ITEM-003", "Name": "Office Chair Ergonomic", "Category": "Furniture", "Branch": "Branch A", "Price": 4500, "Qty": 8, "Min_Qty": 3}
    ])

if 'history' not in st.session_state:
    st.session_state['history'] = pd.DataFrame(columns=["Date", "Type", "SKU", "Name", "Qty", "Branch", "User", "Note"])

if 'admins' not in st.session_state:
    st.session_state['admins'] = pd.DataFrame([
        {"Username": "boss_admin", "Name": "Mr. Boss (Foreigner)", "Branch": "All Branches", "Role": "Super Admin"},
        {"Username": "manager_a", "Name": "คุณสมชาย ใจดี", "Branch": "Headquarter", "Role": "Manager"},
        {"Username": "staff_a", "Name": "คุณสมหญิง รักงาน", "Branch": "Branch A", "Role": "Staff"}
    ])

if 'purchase_requests' not in st.session_state:
    st.session_state['purchase_requests'] = pd.DataFrame(columns=["PR_ID", "Date", "SKU", "Name", "Qty", "Supplier", "Branch", "Status", "Requester"])

# ----------------------------------------------------
# 2. Sidebar: ตั้งค่าภาษาและข้อมูลผู้ใช้
# ----------------------------------------------------
with st.sidebar:
    selected_lang_label = st.selectbox("🌐 Language / ภาษา", ["ไทย (Thai)", "English"], index=0 if st.session_state['lang']=='th' else 1)
    st.session_state['lang'] = 'th' if "Thai" in selected_lang_label else 'en'
    t = LANG[st.session_state['lang']]
    
    st.markdown("---")
    st.markdown(f"**{t['sidebar_user']}**")
    
    admin_list = st.session_state['admins']['Username'].tolist()
    current_user_name = st.selectbox("Switch User (Test Role):", admin_list)
    user_info = st.session_state['admins'][st.session_state['admins']['Username'] == current_user_name].iloc[0]
    
    st.info(f"**{user_info['Name']}**\n\n{t['branch_label']} {user_info['Branch']}\n\n{t['role_label']} {user_info['Role']}")
    st.markdown("---")
    
    st.markdown(f"### {t['menu']}")
    menu_options = [
        t['m_dashboard'],
        t['m_inventory'],
        t['m_import'],
        t['m_export'],
        t['m_history'],
        t['m_pr_po'],
        t['m_admin']
    ]
    selected_menu = st.radio("Navigation", menu_options, label_visibility="collapsed")

# ----------------------------------------------------
# 3. แดชบอร์ดภาพรวม (Dashboard)
# ----------------------------------------------------
if selected_menu == t['m_dashboard']:
    st.title(f"📊 {t['m_dashboard']}")
    
    inv = st.session_state['inventory']
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Items / สินค้าทั้งหมด", len(inv))
    with col2:
        st.metric("Total Stock Qty / จำนวนรวม", int(inv['Qty'].sum()))
    with col3:
        total_val = (inv['Price'] * inv['Qty']).sum()
        st.metric("Total Value / มูลค่ารวม (THB)", f"{total_val:,.2f}")
    with col4:
        low_stock = len(inv[inv['Qty'] <= inv['Min_Qty']])
        st.metric("Low Stock Alerts / สินค้าใกล้หมด", low_stock, delta=-low_stock if low_stock>0 else 0, delta_color="inverse")
    
    st.markdown("---")
    st.subheader("📦 Inventory Status / สถานะสินค้าคงคลัง")
    st.dataframe(inv, use_container_width=True)

# ----------------------------------------------------
# 4. จัดการรายการสินค้า (Master Inventory + Edit / Delete)
# ----------------------------------------------------
elif selected_menu == t['m_inventory']:
    st.title(f"📦 {t['m_inventory']}")
    
    inv = st.session_state['inventory']
    is_readonly = user_info['Role'] == "View Only"
    
    tab_inv1, tab_inv2 = st.tabs(["📋 รายการสินค้าทั้งหมด & แก้ไข/ลบ", "➕ เพิ่มสินค้าใหม่"])
    
    with tab_inv1:
        st.subheader("Product List & Management / รายการสินค้าและการจัดการ")
        if len(inv) > 0:
            st.dataframe(inv, use_container_width=True)
            
            if not is_readonly:
                st.markdown("---")
                st.subheader("✏️ แก้ไข หรือ 🗑️ ลบข้อมูลสินค้า")
                selected_sku_edit = st.selectbox("เลือก SKU สินค้าที่ต้องการแก้ไขหรือลบ", inv['SKU'].tolist())
                
                prod_data = inv[inv['SKU'] == selected_sku_edit].iloc[0]
                
                with st.form("edit_product_form"):
                    e_name = st.text_input("Product Name / ชื่อสินค้า", value=prod_data['Name'])
                    e_cat = st.text_input("Category / หมวดหมู่", value=prod_data['Category'])
                    e_branch = st.selectbox("Branch / สาขา", ["Headquarter", "Branch A", "Branch B"], index=["Headquarter", "Branch A", "Branch B"].index(prod_data['Branch']) if prod_data['Branch'] in ["Headquarter", "Branch A", "Branch B"] else 0)
                    e_price = st.number_input("Unit Price / ราคา", min_value=0.0, value=float(prod_data['Price']))
                    e_min = st.number_input("Min Qty Alert / แจ้งเตือนขั้นต่ำ", min_value=0, value=int(prod_data['Min_Qty']))
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        update_btn = st.form_submit_button("💾 บันทึกการแก้ไข (Update)")
                    with col_btn2:
                        delete_btn = st.form_submit_button("🗑️ ลบสินค้าออกจากระบบ (Delete)")
                        
                    if update_btn:
                        idx = inv[inv['SKU'] == selected_sku_edit].index[0]
                        st.session_state['inventory'].loc[idx, 'Name'] = e_name
                        st.session_state['inventory'].loc[idx, 'Category'] = e_cat
                        st.session_state['inventory'].loc[idx, 'Branch'] = e_branch
                        st.session_state['inventory'].loc[idx, 'Price'] = e_price
                        st.session_state['inventory'].loc[idx, 'Min_Qty'] = e_min
                        st.success(f"อัปเดตข้อมูล SKU: {selected_sku_edit} เรียบร้อยแล้ว!")
                        st.rerun()
                        
                    if delete_btn:
                        st.session_state['inventory'] = inv[inv['SKU'] != selected_sku_edit].reset_index(drop=True)
                        st.warning(f"ลบสินค้า SKU: {selected_sku_edit} ออกจากระบบแล้ว!")
                        st.rerun()
            else:
                st.warning("⚠️ สิทธิ์ของคุณเป็น 'View Only' ไม่สามารถแก้ไขหรือลบข้อมูลได้")
        else:
            st.info("ไม่มีสินค้าในระบบ")

    with tab_inv2:
        if not is_readonly:
            with st.form("add_product_form"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    new_sku = st.text_input("SKU Code")
                    new_name = st.text_input("Product Name / ชื่อสินค้า")
                with c2:
                    new_cat = st.text_input("Category / หมวดหมู่")
                    new_branch = st.selectbox("Branch / สาขา", ["Headquarter", "Branch A", "Branch B"])
                with c3:
                    new_price = st.number_input("Unit Price / ราคาต่อหน่วย", min_value=0.0, value=100.0)
                    new_qty = st.number_input("Initial Qty / จำนวนเริ่มต้น", min_value=0, value=10)
                    new_min = st.number_input("Min Qty Alert / แจ้งเตือนขั้นต่ำ", min_value=0, value=5)
                
                submit_btn = st.form_submit_button("Save Product / บันทึกสินค้า")
                if submit_btn:
                    if new_sku and new_name:
                        if new_sku in inv['SKU'].values:
                            st.error("SKU นี้มีอยู่ในระบบแล้ว!")
                        else:
                            new_row = {"SKU": new_sku, "Name": new_name, "Category": new_cat, "Branch": new_branch, "Price": new_price, "Qty": new_qty, "Min_Qty": new_min}
                            st.session_state['inventory'] = pd.concat([inv, pd.DataFrame([new_row])], ignore_index=True)
                            st.success("Added successfully! / เพิ่มสินค้าเรียบร้อยแล้ว")
                            st.rerun()
                    else:
                        st.warning("Please fill SKU and Product Name / กรุณากรอกรหัสและชื่อสินค้า")
        else:
            st.warning("⚠️ Your permission is 'View Only'.")

# ----------------------------------------------------
# 5. นำเข้าสินค้า (Stock In)
# ----------------------------------------------------
elif selected_menu == t['m_import']:
    st.title("📥 นำเข้าสินค้าเข้าคลัง (Stock In)")
    
    if user_info['Role'] == "View Only":
        st.warning("⚠️ คุณไม่มีสิทธิ์ทำรายการนี้")
    else:
        inv = st.session_state['inventory']
        if len(inv) == 0:
            st.warning("ไม่มีสินค้าในระบบ")
        else:
            with st.form("stock_in_form"):
                selected_sku = st.selectbox("เลือกสินค้า (SKU)", inv['SKU'].tolist())
                prod_row = inv[inv['SKU'] == selected_sku].iloc[0]
                
                st.write(f"**ชื่อสินค้า:** {prod_row['Name']} | **จำนวนคงเหลือปัจจุบัน:** {prod_row['Qty']} | **สาขา:** {prod_row['Branch']}")
                
                import_qty = st.number_input("จำนวนที่ต้องการนำเข้า", min_value=1, value=10)
                note = st.text_input("หมายเหตุ / แหล่งที่มา (เช่น ซื้อจาก Supplier A)")
                
                submit_in = st.form_submit_button("📥 ยืนยันการนำเข้าสินค้า")
                
                if submit_in:
                    idx = inv[inv['SKU'] == selected_sku].index[0]
                    st.session_state['inventory'].loc[idx, 'Qty'] += import_qty
                    
                    new_hist = {
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Type": "IMPORT (นำเข้า)",
                        "SKU": selected_sku,
                        "Name": prod_row['Name'],
                        "Qty": import_qty,
                        "Branch": prod_row['Branch'],
                        "User": user_info['Name'],
                        "Note": note if note else "-"
                    }
                    st.session_state['history'] = pd.concat([st.session_state['history'], pd.DataFrame([new_hist])], ignore_index=True)
                    st.success("นำเข้าสินค้าสำเร็จ!")
                    st.rerun()

# ----------------------------------------------------
# 6. ระบบเบิกสินค้า (Stock Out / Withdrawal System)
# ----------------------------------------------------
elif selected_menu == t['m_export']:
    st.title("📤 ระบบเบิกสินค้าออก (Stock Out & Withdrawal)")
    
    if user_info['Role'] == "View Only":
        st.warning("⚠️ คุณไม่มีสิทธิ์ทำรายการเบิกสินค้า")
    else:
        inv = st.session_state['inventory']
        if len(inv) == 0:
            st.warning("ไม่มีสินค้าในระบบ")
        else:
            with st.form("stock_out_form"):
                st.subheader("แบบฟอร์มเบิกจ่ายสินค้า / Requisition Form")
                
                selected_sku_out = st.selectbox("เลือกสินค้าที่ต้องการเบิก (SKU)", inv['SKU'].tolist())
                prod_row_out = inv[inv['SKU'] == selected_sku_out].iloc[0]
                
                st.info(f"📦 **สินค้า:** {prod_row_out['Name']} | **คงเหลือในคลัง:** {prod_row_out['Qty']} ชิ้น | **สาขาต้นทาง:** {prod_row_out['Branch']}")
                
                col_out1, col_out2 = st.columns(2)
                with col_out1:
                    export_qty = st.number_input("จำนวนที่ต้องการเบิก", min_value=1, value=1)
                    receiver_name = st.text_input("ชื่อผู้เบิก / แผนกที่นำไปใช้")
                with col_out2:
                    destination_branch = st.selectbox("สาขา/หน่วยงานที่รับปลายทาง", ["Headquarter", "Branch A", "Branch B", "External Project"])
                    export_note = st.text_input("วัตถุประสงค์ในการเบิก (Note)")
                
                submit_out = st.form_submit_button("📤 ยืนยันการเบิกสินค้า (Confirm Withdrawal)")
                
                if submit_out:
                    if export_qty > prod_row_out['Qty']:
                        st.error(f"❌ เบิกไม่สำเร็จ! จำนวนสินค้าคงเหลือ ({prod_row_out['Qty']}) ไม่พอสำหรับจำนวนที่ต้องการเบิก ({export_qty})")
                    else:
                        idx = inv[inv['SKU'] == selected_sku_out].index[0]
                        st.session_state['inventory'].loc[idx, 'Qty'] -= export_qty
                        
                        new_hist = {
                            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Type": "EXPORT (เบิกออก)",
                            "SKU": selected_sku_out,
                            "Name": prod_row_out['Name'],
                            "Qty": export_qty,
                            "Branch": f"{prod_row_out['Branch']} ➔ {destination_branch}",
                            "User": f"{user_info['Name']} (ผู้เบิก: {receiver_name})",
                            "Note": export_note if export_note else "-"
                        }
                        st.session_state['history'] = pd.concat([st.session_state['history'], pd.DataFrame([new_hist])], ignore_index=True)
                        st.success(f"✅ เบิกสินค้า {prod_row_out['Name']} จำนวน {export_qty} ชิ้น สำเร็จเรียบร้อย!")
                        st.rerun()

# ----------------------------------------------------
# 7. ประวัติการทำรายการ (Transaction History)
# ----------------------------------------------------
elif selected_menu == t['m_history']:
    st.title(f"📜 {t['m_history']}")
    st.dataframe(st.session_state['history'], use_container_width=True)

# ----------------------------------------------------
# 8. ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)
# ----------------------------------------------------
elif selected_menu == t['m_pr_po']:
    st.title(f"📝 {t['m_pr_po']}")
    
    tab1, tab2 = st.tabs(["📋 สร้างคำขอซื้อ (PR)", "📄 ออกใบสั่งซื้อ (PO)"])
    
    with tab1:
        st.subheader("Create Purchase Request (PR)")
        inv = st.session_state['inventory']
        
        with st.form("pr_form"):
            c1, c2 = st.columns(2)
            with c1:
                pr_sku = st.selectbox("Select Item / เลือกสินค้า", inv['SKU'].tolist()) if len(inv)>0 else st.text_input("SKU")
                pr_qty = st.number_input("Order Qty / จำนวน", min_value=1, value=10)
            with c2:
                pr_supplier = st.text_input("Supplier Name / ชื่อผู้จัดจำหน่าย")
                pr_branch = st.selectbox("Destination Branch / สาขา", ["Headquarter", "Branch A", "Branch B"])
            
            submit_pr = st.form_submit_button("Submit PR / ส่งคำขอซื้อ")
            if submit_pr:
                if pr_supplier:
                    pr_id = f"PR-{datetime.now().strftime('%Y%m%d%H%M')}"
                    p_name = inv[inv['SKU'] == pr_sku]['Name'].values[0] if len(inv)>0 and pr_sku in inv['SKU'].values else "Custom Item"
                    new_pr = {
                        "PR_ID": pr_id,
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "SKU": pr_sku,
                        "Name": p_name,
                        "Qty": pr_qty,
                        "Supplier": pr_supplier,
                        "Branch": pr_branch,
                        "Status": "Pending (รออนุมัติ)",
                        "Requester": user_info['Name']
                    }
                    st.session_state['purchase_requests'] = pd.concat([st.session_state['purchase_requests'], pd.DataFrame([new_pr])], ignore_index=True)
                    st.success(f"PR Created: {pr_id}")
                else:
                    st.warning("Please enter Supplier name")
        
        st.markdown("---")
        pr_df = st.session_state['purchase_requests']
        st.dataframe(pr_df, use_container_width=True)
        
        if len(pr_df) > 0 and user_info['Role'] in ["Super Admin", "Manager"]:
            st.markdown("#### ⚡ Approval Action")
            pending_prs = pr_df[pr_df['Status'] == "Pending (รออนุมัติ)"]['PR_ID'].tolist()
            if pending_prs:
                selected_pr_id = st.selectbox("Select PR ID", pending_prs)
                col_app1, col_app2 = st.columns(2)
                with col_app1:
                    if st.button("✅ Approve"):
                        idx = pr_df[pr_df['PR_ID'] == selected_pr_id].index[0]
                        st.session_state['purchase_requests'].loc[idx, 'Status'] = "Approved (อนุมัติแล้ว)"
                        st.success("Approved!")
                        st.rerun()
                with col_app2:
                    if st.button("❌ Reject"):
                        idx = pr_df[pr_df['PR_ID'] == selected_pr_id].index[0]
                        st.session_state['purchase_requests'].loc[idx, 'Status'] = "Rejected (ไม่อนุมัติ)"
                        st.rerun()

    with tab2:
        st.subheader("Generate Purchase Order (PO)")
        pr_df = st.session_state['purchase_requests']
        approved_prs = pr_df[pr_df['Status'] == "Approved (อนุมัติแล้ว)"]
        
        if len(approved_prs) == 0:
            st.info("No approved PR available.")
        else:
            selected_po_pr = st.selectbox("Select Approved PR", approved_prs['PR_ID'].tolist())
            pr_row = approved_prs[approved_prs['PR_ID'] == selected_po_pr].iloc[0]
            
            inv = st.session_state['inventory']
            item_price = inv[inv['SKU'] == pr_row['SKU']]['Price'].values[0] if len(inv)>0 and pr_row['SKU'] in inv['SKU'].values else 100.0
            total_amount = item_price * pr_row['Qty']
            
            po_html = f"""
            <div style="border: 2px solid #333; padding: 25px; border-radius: 10px; background-color: #fff; color: #000;">
                <h2 style="text-align: center; margin-bottom: 0;">PURCHASE ORDER (PO)</h2>
                <h4 style="text-align: center; color: gray; margin-top: 5px;">ใบสั่งซื้อสินค้า</h4>
                <hr>
                <p><b>PO ID:</b> PO-{pr_row['PR_ID']}</p>
                <p><b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}</p>
                <p><b>Supplier:</b> {pr_row['Supplier']}</p>
                <p><b>Branch:</b> {pr_row['Branch']}</p>
                <br>
                <table width="100%" border="1" cellspacing="0" cellpadding="8" style="border-collapse: collapse; text-align: left;">
                    <tr style="background-color: #f2f2f2;">
                        <th>SKU</th>
                        <th>Product Description</th>
                        <th>Qty</th>
                        <th>Unit Price</th>
                        <th>Total</th>
                    </tr>
                    <tr>
                        <td>{pr_row['SKU']}</td>
                        <td>{pr_row['Name']}</td>
                        <td>{pr_row['Qty']}</td>
                        <td>{item_price:,.2f}</td>
                        <td>{total_amount:,.2f}</td>
                    </tr>
                </table>
                <br>
                <h3 style="text-align: right;">Grand Total: {total_amount:,.2f} THB</h3>
            </div>
            """
            st.markdown(po_html, unsafe_allow_html=True)
            st.markdown("---")
            st.download_button(
                label="📥 Download Purchase Order (HTML)",
                data=po_html,
                file_name=f"PO_{pr_row['PR_ID']}.html",
                mime="text/html"
            )

# ----------------------------------------------------
# 9. จัดการแอดมินและสิทธิ์ (Admin & Permissions)
# ----------------------------------------------------
elif selected_menu == t['m_admin']:
    st.title(f"⚙️ {t['m_admin']}")
    
    if user_info['Role'] != "Super Admin":
        st.error("Access Denied! Only Super Admin can access this menu.")
    else:
        st.subheader("Admin Accounts & Branch Permissions")
        st.dataframe(st.session_state['admins'], use_container_width=True)
        
        st.markdown("---")
        st.subheader("➕ Add New Admin")
        with st.form("add_admin_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_username = st.text_input("Username (ID)")
                new_admin_name = st.text_input("Full Name")
            with c2:
                new_admin_branch = st.selectbox("Assigned Branch", ["Headquarter", "Branch A", "Branch B", "All Branches"])
                new_admin_role = st.selectbox("Role", ["Super Admin", "Manager", "Staff", "View Only"])
            
            submit_admin = st.form_submit_button("Save Admin")
            if submit_admin:
                if new_username and new_admin_name:
                    admins_df = st.session_state['admins']
                    if new_username in admins_df['Username'].values:
                        st.error("Username already exists!")
                    else:
                        new_a = {"Username": new_username, "Name": new_admin_name, "Branch": new_admin_branch, "Role": new_admin_role}
                        st.session_state['admins'] = pd.concat([admins_df, pd.DataFrame([new_a])], ignore_index=True)
                        st.success("Admin added successfully!")
                        st.rerun()
                else:
                    st.warning("Please fill all fields")
