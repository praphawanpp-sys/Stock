import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="Enterprise Stock & Multi-Company System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 0. รายชื่อบริษัทและพจนานุกรมภาษา (TH / EN)
# ----------------------------------------------------
COMPANIES = [
    "Daddy Deli (Head Office)",
    "Harvest Cafe (Branch 0001)",
    "Taboo By Daddy Deli (Branch 0002)",
    "Daddy Deli Pattaya Group (Head Office)",
    "Harvest Bakery And Restaurant (Head Office)",
    "Daddy Deli Beach House (Head Office)"
]

LANG = {
    "th": {
        "title": "ระบบจัดการสต็อกวัตถุดิบและคลังสินค้า (Multi-Company)",
        "sidebar_lang": "🌐 เลือกภาษา / Language",
        "sidebar_company": "🏢 เลือกบริษัท / สาขา",
        "sidebar_user": "👤 ผู้ใช้งานปัจจุบัน",
        "role_label": "สิทธิ์:",
        "menu": "📌 เมนูหลัก",
        "m_dashboard": "📊 แดชบอร์ดภาพรวม",
        "m_inventory_mgmt": "📦 การจัดการรายการสินค้า",
        "sub_import_excel": "📥 3.1 นำเข้าสินค้าจาก Excel",
        "sub_stock_in": "📥 3.2 รับสินค้า (Stock In)",
        "sub_stock_out": "📤 3.3 เบิกสินค้า (Stock Out)",
        "m_history": "📜 ประวัติการทำรายการ",
        "m_pr_po": "📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)",
        "m_eom": "📋 รายการสรุปสต็อก & นับสต็อกสิ้นเดือน",
        "m_admin": "⚙️ จัดการแอดมินและสิทธิ์",
    },
    "en": {
        "title": "Enterprise Food Cost & Stock Management System",
        "sidebar_lang": "🌐 Select Language / ภาษา",
        "sidebar_company": "🏢 Select Company / Branch",
        "sidebar_user": "👤 Current User",
        "role_label": "Role:",
        "menu": "📌 Main Menu",
        "m_dashboard": "📊 Dashboard & Overview",
        "m_inventory_mgmt": "📦 Inventory Management",
        "sub_import_excel": "📥 3.1 Import from Excel",
        "sub_stock_in": "📥 3.2 Stock In",
        "sub_stock_out": "📤 3.3 Stock Out / Requisition",
        "m_history": "📜 Transaction History",
        "m_pr_po": "📝 Purchase Request (PR) & PO",
        "m_eom": "📋 Stock Summary & End of Month Count",
        "m_admin": "⚙️ Admin & Permissions",
    }
}

# พจนานุกรมแปลชื่อวัตถุดิบและหมวดหมู่เป็นอังกฤษอัตโนมัติ
TRANSLATE_DICT = {
    "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others": "Meat / Seasonings / Others",
    "ผักและผลไม้ / Vegetables & Fruits": "Vegetables & Fruits",
    "ทะเล / Seafood": "Seafood",
    "เนื้อวัว / Beef": "Beef",
    "น้ำผลไม้/Soft Drink/อื่นๆ / Juice/Soft Drink/Other": "Juice / Soft Drink / Other",
    "เบียร์ / Beer": "Beer",
    "เนื้อแกะ / Lamb": "Lamb",
    "ไวน์ / Wine": "Wine",
    "ขนมปัง / Bread": "Bread",
    "ของหวาน / Dessert": "Dessert",
    "เมล็ดกาแฟ / Coffee Beans": "Coffee Beans"
}

# ----------------------------------------------------
# 1. จัดการ Session State (ฐานข้อมูลจำลอง)
# ----------------------------------------------------
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'th'

if 'company_inventories' not in st.session_state:
    st.session_state['company_inventories'] = {}
    for comp in COMPANIES:
        st.session_state['company_inventories'][comp] = pd.DataFrame(columns=[
            "Product Code", "Item Name", "Category", "Unit", "Stock Balance", "Last Price", "Supplier"
        ])
    # ใส่ข้อมูลตัวอย่างให้บริษัทแรก
    st.session_state['company_inventories'][COMPANIES[0]] = pd.DataFrame([
        {"Product Code": "422582", "Item Name": "นมจืด 1 ลิตร", "Category": "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others", "Unit": "Box", "Stock Balance": 25.0, "Last Price": 109.0, "Supplier": "CP Axtra (Makro)"},
        {"Product Code": "2502009877754", "Item Name": "กระเทียมดัดจุก 500 ก.", "Category": "ผักและผลไม้ / Vegetables & Fruits", "Unit": "Pack", "Stock Balance": 10.0, "Last Price": 40.0, "Supplier": "CP Axtra (Lotus)"}
    ])

if 'transactions' not in st.session_state:
    st.session_state['transactions'] = pd.DataFrame([
        {"Company": COMPANIES[0], "Date": str(datetime.today().date()), "Supplier": "CP Axtra (Makro)", "Item Name": "นมจืด 1 ลิตร", "Quantity": 25.0, "Price/Unit": 109.0, "Vat Type": "Non Vat", "Total Price": 2725.0, "Type": "IMPORT"}
    ])

if 'admins' not in st.session_state:
    st.session_state['admins'] = pd.DataFrame([
        {"Username": "boss_admin", "Name": "Mr. Boss (Foreigner)", "Branch": "All Branches", "Role": "Super Admin"},
        {"Username": "manager_a", "Name": "คุณสมชาย ใจดี", "Branch": COMPANIES[0], "Role": "Manager"}
    ])

if 'purchase_requests' not in st.session_state:
    st.session_state['purchase_requests'] = pd.DataFrame(columns=["PR_ID", "Date", "SKU", "Name", "Qty", "Supplier", "Branch", "Status", "Requester"])

# ----------------------------------------------------
# 2. Sidebar: เลือกภาษา บริษัท และผู้ใช้งาน
# ----------------------------------------------------
with st.sidebar:
    selected_lang_label = st.selectbox("🌐 Language / ภาษา", ["ไทย (Thai)", "English"], index=0 if st.session_state['lang']=='th' else 1)
    st.session_state['lang'] = 'th' if "Thai" in selected_lang_label else 'en'
    t = LANG[st.session_state['lang']]
    
    st.markdown("---")
    selected_company = st.selectbox(f"🏢 {t['sidebar_company']}", COMPANIES)
    
    st.markdown("---")
    st.markdown(f"**{t['sidebar_user']}**")
    admin_list = st.session_state['admins']['Username'].tolist()
    current_user_name = st.selectbox("Switch User:", admin_list)
    user_info = st.session_state['admins'][st.session_state['admins']['Username'] == current_user_name].iloc[0]
    st.info(f"**{user_info['Name']}**\n\n{t['role_label']} {user_info['Role']}")
    
    st.markdown("---")
    st.markdown(f"### {t['menu']}")
    
    selected_menu = st.radio("Navigation", [
        t['m_dashboard'],
        t['m_inventory_mgmt'],
        t['sub_import_excel'],
        t['sub_stock_in'],
        t['sub_stock_out'],
        t['m_history'],
        t['m_pr_po'],
        t['m_eom'],
        t['m_admin']
    ], label_visibility="collapsed")

# ดึงข้อมูลสต็อกและประวัติของบริษัทที่เลือกปัจจุบัน
current_inv = st.session_state['company_inventories'][selected_company]
trans_df = st.session_state['transactions']

# ฟังก์ชันแปลงชื่อตามภาษาที่เลือก
def localize_text(text):
    if st.session_state['lang'] == 'en':
        return TRANSLATE_DICT.get(text, text)
    return text

# ----------------------------------------------------
# 3. เมนูที่ 1: แดชบอร์ดภาพรวม พร้อมตัวกรองร้านค้าและวันที่
# ----------------------------------------------------
if selected_menu == t['m_dashboard']:
    st.title(f"📊 {t['m_dashboard']} - {selected_company}")
    
    st.markdown("#### 🔍 ตัวกรองข้อมูล (Filters)")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        suppliers_list = ["All Suppliers / ทุกร้านค้า"] + (trans_df['Supplier'].unique().tolist() if len(trans_df)>0 else [])
        selected_supplier_filter = st.selectbox("Supplier / ร้านค้าที่ซื้อ", suppliers_list)
    with col_f2:
        start_date = st.date_input("Start Date / ตั้งแต่วันที่", value=datetime.today().replace(day=1))
    with col_f3:
        end_date = st.date_input("End Date / ถึงวันที่", value=datetime.today())
        
    st.markdown("---")
    
    # กรองข้อมูลตามเงื่อนไข
    filtered_inv = current_inv.copy()
    if len(trans_df) > 0:
        comp_trans = trans_df[(trans_df['Company'] == selected_company)].copy()
        comp_trans['Date_dt'] = pd.to_datetime(comp_trans['Date'], errors='coerce')
        
        # กรองวันที่และ Supplier
        mask = (comp_trans['Date_dt'].dt.date >= start_date) & (comp_trans['Date_dt'].dt.date <= end_date)
        if selected_supplier_filter != "All Suppliers / ทุกร้านค้า":
            mask &= (comp_trans['Supplier'] == selected_supplier_filter)
        filtered_trans = comp_trans[mask]
    else:
        filtered_trans = pd.DataFrame()

    total_items = len(filtered_inv)
    total_qty = filtered_inv['Stock Balance'].sum() if total_items > 0 else 0
    total_val = (filtered_inv['Stock Balance'] * filtered_inv['Last Price']).sum() if total_items > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Items / จำนวนรายการวัตถุดิบ", f"{total_items} Items")
    with col2:
        st.metric("Total Stock Balance / สต็อกคงเหลือรวม", f"{total_qty:,.2f}")
    with col3:
        st.metric("Estimated Stock Value / มูลค่าสต็อกรวม", f"{total_val:,.2f} THB")
        
    st.subheader("📦 Inventory Data Table / ตารางข้อมูลวัตถุดิบ")
    if len(filtered_inv) > 0:
        display_inv = filtered_inv.copy()
        if st.session_state['lang'] == 'en':
            display_inv['Category'] = display_inv['Category'].apply(localize_text)
        st.dataframe(display_inv, use_container_width=True)
    else:
        st.info("No inventory data found for this selection.")

# ----------------------------------------------------
# 4. เมนูย่อย 3.1: นำเข้าสินค้าจาก Excel (Import Excel)
# ----------------------------------------------------
elif selected_menu == t['sub_import_excel']:
    st.title(f"📥 {t['sub_import_excel']} - {selected_company}")
    
    st.write("รูปแบบไฟล์: คอลัมน์ 0=Supplier, คอลัมน์ 1=รหัสสินค้า, คอลัมน์ 2=ชื่อวัตถุดิบ, คอลัมน์ 3=ราคา, คอลัมน์ 4=หน่วยนับ")
    uploaded_file = st.file_uploader("เลือกไฟล์ Excel / Choose Excel File", type=["xlsx", "xls", "csv"])
    
    if uploaded_file is not None:
        try:
            df_raw = pd.read_csv(uploaded_file, header=None) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file, header=None)
            st.write(f"พบข้อมูลทั้งหมด: {len(df_raw)} แถว (แสดงตัวอย่าง 5 แถวแรก):")
            st.dataframe(df_raw.head())
            
            if st.button("ยืนยันการนำเข้าข้อมูลเข้าสู่ระบบ / Confirm Import"):
                new_items_list = []
                for index, row in df_raw.iloc[1:].iterrows():
                    supplier = str(row.get(0, "General"))
                    p_code = str(row.get(1, "AUTO"))
                    i_name = str(row.get(2, ""))
                    try:
                        price = float(row.get(3, 0.0)) if pd.notna(row.get(3)) else 0.0
                    except:
                        price = 0.0
                    unit = str(row.get(4, "Pcs.")) if pd.notna(row.get(4)) else "Pcs."
                    
                    if pd.notna(i_name) and i_name.strip() != "" and i_name != "nan":
                        new_items_list.append({
                            "Product Code": p_code,
                            "Item Name": i_name,
                            "Category": "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others",
                            "Unit": unit,
                            "Stock Balance": 0.0,
                            "Last Price": price,
                            "Supplier": supplier
                        })
                
                if len(new_items_list) > 0:
                    df_import = pd.DataFrame(new_items_list)
                    st.session_state['company_inventories'][selected_company] = pd.concat([current_inv, df_import], ignore_index=True).drop_duplicates(subset=["Item Name"], keep="last")
                    st.success(f"นำเข้าสำเร็จ {len(new_items_list)} รายการ!")
                    st.rerun()
                else:
                    st.error("ไม่พบข้อมูลชื่อสินค้าในไฟล์")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

# ----------------------------------------------------
# 5. เมนูย่อย 3.2: รับสินค้า (Stock In)
# ----------------------------------------------------
elif selected_menu == t['sub_stock_in']:
    st.title(f"📥 {t['sub_stock_in']} - {selected_company}")
    
    if len(current_inv) > 0:
        with st.form("stock_in_form"):
            selected_item = st.selectbox("เลือกวัตถุดิบ / Select Item", current_inv['Item Name'].tolist())
            supplier_in = st.text_input("Supplier Name / ชื่อร้านค้าที่ซื้อ")
            qty_in = st.number_input("Quantity / จำนวนรับเข้า", min_value=0.1, value=1.0)
            price_in = st.number_input("Price per Unit / ราคาต่อหน่วย", min_value=0.0, value=10.0)
            
            submit_in = st.form_submit_button("บันทึกรับเข้าสินค้า / Confirm Stock In")
            if submit_in:
                idx = current_inv[current_inv['Item Name'] == selected_item].index[0]
                st.session_state['company_inventories'][selected_company].loc[idx, 'Stock Balance'] += qty_in
                st.session_state['company_inventories'][selected_company].loc[idx, 'Last Price'] = price_in
                if supplier_in:
                    st.session_state['company_inventories'][selected_company].loc[idx, 'Supplier'] = supplier_in
                
                new_t = {
                    "Company": selected_company, "Date": str(datetime.today().date()),
                    "Supplier": supplier_in if supplier_in else "General", "Item Name": selected_item,
                    "Quantity": qty_in, "Price/Unit": price_in, "Vat Type": "Non Vat",
                    "Total Price": qty_in * price_in, "Type": "IMPORT"
                }
                st.session_state['transactions'] = pd.concat([st.session_state['transactions'], pd.DataFrame([new_t])], ignore_index=True)
                st.success("บันทึกรับเข้าสินค้าเรียบร้อย!")
                st.rerun()
    else:
        st.warning("ยังไม่มีรายการสินค้าในสาขานี้ กรุณานำเข้าหรือเพิ่มสินค้าก่อน")

# ----------------------------------------------------
# 6. เมนูย่อย 3.3: เบิกสินค้า (Stock Out)
# ----------------------------------------------------
elif selected_menu == t['sub_stock_out']:
    st.title(f"📤 {t['sub_stock_out']} - {selected_company}")
    
    if len(current_inv) > 0:
        with st.form("stock_out_form"):
            selected_item_out = st.selectbox("เลือกวัตถุดิบที่ต้องการเบิก / Select Item", current_inv['Item Name'].tolist())
            item_row = current_inv[current_inv['Item Name'] == selected_item_out].iloc[0]
            st.info(f"คงเหลือปัจจุบัน: {item_row['Stock Balance']} {item_row['Unit']}")
            
            qty_out = st.number_input("จำนวนที่ต้องการเบิก / Withdrawal Qty", min_value=0.1, value=1.0)
            receiver = st.text_input("ชื่อผู้เบิก / แผนกที่นำไปใช้")
            
            submit_out = st.form_submit_button("ยืนยันการเบิกสินค้า / Confirm Withdrawal")
            if submit_out:
                if qty_out > item_row['Stock Balance']:
                    st.error("จำนวนคงเหลือไม่พอเบิกออก!")
                else:
                    idx = current_inv[current_inv['Item Name'] == selected_item_out].index[0]
                    st.session_state['company_inventories'][selected_company].loc[idx, 'Stock Balance'] -= qty_out
                    
                    new_t = {
                        "Company": selected_company, "Date": str(datetime.today().date()),
                        "Supplier": item_row['Supplier'], "Item Name": selected_item_out,
                        "Quantity": qty_out, "Price/Unit": item_row['Last Price'], "Vat Type": "Non Vat",
                        "Total Price": qty_out * item_row['Last Price'], "Type": "EXPORT"
                    }
                    st.session_state['transactions'] = pd.concat([st.session_state['transactions'], pd.DataFrame([new_t])], ignore_index=True)
                    st.success("เบิกสินค้าสำเร็จ!")
                    st.rerun()
    else:
        st.warning("ไม่มีสินค้าในระบบ")

# ----------------------------------------------------
# 7. ประวัติการทำรายการ (History)
# ----------------------------------------------------
elif selected_menu == t['m_history']:
    st.title(f"📜 {t['m_history']} - {selected_company}")
    if len(trans_df) > 0:
        comp_trans = trans_df[trans_df['Company'] == selected_company]
        st.dataframe(comp_trans, use_container_width=True)
    else:
        st.info("ยังไม่มีประวัติการทำรายการ")

# ----------------------------------------------------
# 8. ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)
# ----------------------------------------------------
elif selected_menu == t['m_pr_po']:
    st.title(f"📝 {t['m_pr_po']} - {selected_company}")
    tab1, tab2 = st.tabs(["📋 สร้างใบขอซื้อ (PR)", "📄 ออกใบสั่งซื้อ (PO)"])
    with tab1:
        with st.form("pr_form"):
            pr_item = st.text_input("ชื่อวัตถุดิบที่ต้องการสั่งซื้อ")
            pr_qty = st.number_input("จำนวน", min_value=1.0, value=10.0)
            pr_sup = st.text_input("ชื่อ Supplier / ร้านค้า")
            sub_pr = st.form_submit_button("ส่งคำขอซื้อ (Submit PR)")
            if sub_pr and pr_item and pr_sup:
                new_pr = {
                    "PR_ID": f"PR-{datetime.now().strftime('%m%d%H%M')}",
                    "Date": str(datetime.today()), "SKU": "AUTO", "Name": pr_item,
                    "Qty": pr_qty, "Supplier": pr_sup, "Branch": selected_company,
                    "Status": "Pending (รออนุมัติ)", "Requester": user_info['Name']
                }
                st.session_state['purchase_requests'] = pd.concat([st.session_state['purchase_requests'], pd.DataFrame([new_pr])], ignore_index=True)
                st.success("สร้าง PR สำเร็จ!")
                st.rerun()
        st.dataframe(st.session_state['purchase_requests'], use_container_width=True)
    with tab2:
        st.write("เลือก PR ที่ได้รับการอนุมัติเพื่อพิมพ์ใบ PO ทางการ")

# ----------------------------------------------------
# 9. รายการสรุปสต็อกและนับสต็อกสิ้นเดือน (End of Month Count)
# ----------------------------------------------------
elif selected_menu == t['m_eom']:
    st.title(f"📋 {t['m_eom']} - {selected_company}")
    if len(current_inv) > 0:
        st.write("กรุณากรอกยอดนับจริง (Actual Count) ประจำสิ้นเดือน เพื่อปรับปรุงยอดสต็อกให้ตรงกับหน้างานจริง")
        
        count_df = current_inv[['Item Name', 'Category', 'Unit', 'Stock Balance']].copy()
        count_df.rename(columns={'Stock Balance': 'System Balance (ยอดในระบบ)'}, inplace=True)
        count_df['Actual Count (ยอดนับจริง)'] = count_df['System Balance (ยอดในระบบ)']
        
        edited_df = st.data_editor(
            count_df,
            column_config={"Actual Count (ยอดนับจริง)": st.column_config.NumberColumn(min_value=0.0, step=0.1)},
            disabled=["Item Name", "Category", "Unit", "System Balance (ยอดในระบบ)"],
            use_container_width=True
        )
        
        if st.button("💾 บันทึกและปรับปรุงยอดสต็อกสิ้นเดือน"):
            for idx, row in edited_df.iterrows():
                item_name = row['Item Name']
                actual_val = row['Actual Count (ยอดนับจริง)']
                orig_idx = current_inv[current_inv['Item Name'] == item_name].index[0]
                st.session_state['company_inventories'][selected_company].loc[orig_idx, 'Stock Balance'] = actual_val
            st.success("บันทึกยอดนับสต็อกสิ้นเดือนเรียบร้อยแล้ว!")
            st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลสินค้าในสาขานี้")

# ----------------------------------------------------
# 10. จัดการแอดมินและสิทธิ์ (Admin Management)
# ----------------------------------------------------
elif selected_menu == t['m_admin']:
    st.title(f"⚙️ {t['m_admin']}")
    if user_info['Role'] != "Super Admin":
        st.error("เฉพาะ Super Admin เท่านั้นที่เข้าถึงหน้านี้ได้")
    else:
        st.dataframe(st.session_state['admins'], use_container_width=True)
