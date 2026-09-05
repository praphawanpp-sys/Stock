import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)",
    page_icon="📝",
    layout="wide"
)

# ----------------------------------------------------
# 1. INITIALIZE SESSION STATES
# ----------------------------------------------------
if "units_list" not in st.session_state:
    st.session_state.units_list = ["Box", "Bottle", "Kg", "Pack", "Can", "Piece"]

if "categories_list" not in st.session_state:
    st.session_state.categories_list = ["นม / Milk", "เบเกอรี่ / Bakery", "เครื่องดื่ม / Beverage", "วัตถุดิบอาหาร / Ingredients"]

# รายชื่อบริษัท/สาขาใหม่ตามที่คุณต้องการ
if "companies_list" not in st.session_state:
    st.session_state.companies_list = [
        "Daddy Deli (Head Office)",
        "Harvest Cafe (Branch 0001)",
        "Taboo By Daddy Deli (Branch 0002)",
        "Daddy Deli Pattaya Group (Head Office)",
        "Harvest Bakery And Restaurant (Head Office)",
        "Daddy Deli Beach House (Head Office)"
    ]

if "company_details" not in st.session_state:
    st.session_state["company_details"] = {
        "Daddy Deli (Head Office)": {"name": "Daddy Deli (Head Office)", "address": "กรุงเทพมหานคร", "tax_id": "01055xxxxxxxx", "contact": "02-xxx-xxxx"},
        "Harvest Cafe (Branch 0001)": {"name": "Harvest Cafe (Branch 0001)", "address": "สาขา 0001", "tax_id": "01055yyyyyyyy", "contact": "02-yyy-yyyy"},
        "Taboo By Daddy Deli (Branch 0002)": {"name": "Taboo By Daddy Deli (Branch 0002)", "address": "สาขา 0002", "tax_id": "01055zzzzzzzz", "contact": "02-zzz-zzzz"},
        "Daddy Deli Pattaya Group (Head Office)": {"name": "Daddy Deli Pattaya Group (Head Office)", "address": "พัทยา ชลบุรี", "tax_id": "01055aaaaaaaa", "contact": "038-aaa-aaaa"},
        "Harvest Bakery And Restaurant (Head Office)": {"name": "Harvest Bakery And Restaurant (Head Office)", "address": "กรุงเทพมหานคร", "tax_id": "01055bbbbbbbb", "contact": "02-bbb-bbbb"},
        "Daddy Deli Beach House (Head Office)": {"name": "Daddy Deli Beach House (Head Office)", "address": "ภูเก็ต", "tax_id": "01055cccccccc", "contact": "076-ccc-cccc"}
    }

if "company_logos" not in st.session_state:
    st.session_state["company_logos"] = {}

# กำหนดโครงสร้างข้อมูลสินค้าเริ่มต้นให้ทุกสาขา
if "company_inventories" not in st.session_state:
    initial_demo_df = pd.DataFrame([
        {
            "Product Code": "1950",
            "Item Name": "นมจืด 2 ลิตร",
            "Category": "นม / Milk",
            "Unit": "Bottle",
            "Conversion Qty": 1.0,
            "Stock Balance": 10.0,
            "Last Price": 95.0,
            "Supplier": "CP Axtra (Makro)",
            "Vat Type": "Non Vat"
        }
    ])
    
    st.session_state["company_inventories"] = {}
    for comp in st.session_state.companies_list:
        if comp == "Daddy Deli (Head Office)":
            st.session_state["company_inventories"][comp] = initial_demo_df.copy()
        else:
            st.session_state["company_inventories"][comp] = pd.DataFrame(columns=[
                "Product Code", "Item Name", "Category", "Unit", "Conversion Qty", "Stock Balance", "Last Price", "Supplier", "Vat Type"
            ])

if "purchase_requests" not in st.session_state:
    st.session_state["purchase_requests"] = pd.DataFrame(columns=[
        "PR_ID", "Date", "Supplier", "Branch", "Status", "Requester", "Items_JSON", "Total_Amount"
    ])

if "purchase_orders" not in st.session_state:
    st.session_state["purchase_orders"] = pd.DataFrame(columns=[
        "PO_ID", "PR_ID", "Supplier", "Branch", "Date"
    ])

if "transaction_history" not in st.session_state:
    st.session_state["transaction_history"] = pd.DataFrame(columns=[
        "Date", "Branch", "Type", "Item Name", "Quantity", "Unit", "Note"
    ])

if "temp_stock_in_cart" not in st.session_state:
    st.session_state["temp_stock_in_cart"] = []

VAT_TYPES_LIST = ["Non Vat", "Vat 7%", "Vat Excluded"]

# ----------------------------------------------------
# 2. SIDEBAR CONFIGURATION
# ----------------------------------------------------
st.sidebar.markdown("### 🌐 ภาษา / Language")
lang = st.sidebar.selectbox("Language", ["ไทย (Thai)"], label_visibility="collapsed")

st.sidebar.markdown("### 👤 ผู้ใช้งานปัจจุบัน (Current User)")
current_user = st.sidebar.selectbox("User", ["owner_master", "staff_procurement"], label_visibility="collapsed")
user_info = {"Name": "Mr. Owner" if current_user == "owner_master" else "Staff PR", "Role": "Owner" if current_user == "owner_master" else "Staff"}

# เลือกบริษัท / สาขา
st.sidebar.markdown("### 🏢 เลือกบริษัท / สาขา")
selected_company = st.sidebar.selectbox("Company", st.session_state.companies_list, label_visibility="collapsed")

curr_comp_details = st.session_state["company_details"].get(selected_company, {})
st.sidebar.caption(f"ที่อยู่: {curr_comp_details.get('address', '-')}\n\nเลขผู้เสียภาษี: {curr_comp_details.get('tax_id', '-')}\n\nติดต่อ: {curr_comp_details.get('contact', '-')}")
st.sidebar.info(f"**{user_info['Name']}**\n\nสิทธิ์: {user_info['Role']}")

# ----------------------------------------------------
# 3. MAIN NAVIGATION MENU
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ เมนูหลัก")

t = {
    "sub_dashboard": "📊 แดชบอร์ดภาพรวม",
    "sub_inventory": "📦 การจัดการรายการสินค้า",
    "sub_import_excel": "📥 เพิ่มรายการสินค้าใหม่",
    "sub_stock_in": "📥 รับสินค้า (Stock In)",
    "sub_stock_out": "📤 เบิกสินค้า (Stock Out)",
    "sub_pr_po": "📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)",
    "sub_history": "⏱️ ประวัติการทำรายการ",
    "sub_report": "📈 รายการสรุปสต็อก & นับสต็อก",
    "sub_settings": "⚙️ ตั้งค่าข้อมูลบริษัทและแอดมิน"
}

selected_menu = st.sidebar.radio(
    "Menu",
    list(t.values()),
    label_visibility="collapsed"
)

if selected_company not in st.session_state["company_inventories"]:
    st.session_state["company_inventories"][selected_company] = pd.DataFrame(columns=[
        "Product Code", "Item Name", "Category", "Unit", "Conversion Qty", "Stock Balance", "Last Price", "Supplier", "Vat Type"
    ])
current_inv = st.session_state["company_inventories"][selected_company]

# ----------------------------------------------------
# 4. ROUTING LOGIC
# ----------------------------------------------------

# a) Dashboard
if selected_menu == t["sub_dashboard"]:
    st.title(f"📊 แดชบอร์ดภาพรวม - {selected_company}")
    col1, col2, col3 = st.columns(3)
    col1.metric("จำนวนรายการสินค้าทั้งหมด", f"{len(current_inv)} รายการ")
    col2.metric("ใบขอซื้อ (PR) ทั้งหมด", f"{len(st.session_state['purchase_requests'])} ใบ")
    col3.metric("ใบสั่งซื้อ (PO) ทั้งหมด", f"{len(st.session_state['purchase_orders'])} ใบ")
    st.markdown("---")
    st.subheader("รายการสินค้าในระบบปัจจุบัน")
    if len(current_inv) > 0:
        st.dataframe(current_inv, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลสินค้าในระบบสาขานี้")

# b) Inventory Management (อัปเดตตามคำขอ)
elif selected_menu == t["sub_inventory"]:
    st.title(f"📦 การจัดการรายการสินค้า - {selected_company}")
    st.caption("สรุปสินค้าทั้งหมดของบริษัท/สาขานั้นๆ ว่ามีสินค้าอะไรบ้าง")
    
    if len(current_inv) > 0:
        st.markdown("#### 🔍 ค้นหาข้อมูลสินค้า")
        scol1, scol2, scol3 = st.columns(3)
        with scol1:
            search_supplier = st.text_input("ค้นหาตามชื่อร้านค้า (Supplier)")
        with scol2:
            search_code = st.text_input("ค้นหาตามรหัสสินค้า (Product Code)")
        with scol3:
            # ดึงหมวดหมู่ทั้งหมดที่มีอยู่ในตารางมาให้เลือกค้นหา หรือกรองแบบอิสระ
            cat_options = ["ทั้งหมด"] + current_inv["Category"].dropna().unique().tolist()
            search_category = st.selectbox("ค้นหาตามหมวดหมู่ (Category)", cat_options)

        filtered_df = current_inv.copy()
        if search_supplier:
            filtered_df = filtered_df[filtered_df["Supplier"].astype(str).str.contains(search_supplier, case=False, na=False)]
        if search_code:
            filtered_df = filtered_df[filtered_df["Product Code"].astype(str).str.contains(search_code, case=False, na=False)]
        if search_category != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df["Category"] == search_category]

        st.markdown("---")
        st.subheader("รายชื่อสินค้าในระบบและการจัดการ")

        for idx, row in filtered_df.iterrows():
            cols = st.columns([2.2, 1.2, 1.2, 1.2, 0.9, 0.9, 0.9, 1.3])
            cols[0].write(f"**{row['Item Name']}**")
            cols[1].write(f"รหัส: {row['Product Code']}")
            cols[2].write(f"ร้าน: {row['Supplier']}")
            cols[3].write(f"หมวด: {row['Category']}")
            cols[4].write(f"คงเหลือ: {row['Stock Balance']}")
            cols[5].write(f"หน่วย: {row['Unit']}")
            cols[6].write(f"ราคา: {row['Last Price']} ฿")

            # ดรอปดาวน์ "แก้ไข/ลบ" เล็กๆ ด้านหลังรายการสินค้า
            action_choice = cols[7].selectbox(
                "จัดการ", 
                ["เลือก", "✏️ แก้ไข", "🗑️ ลบ"], 
                key=f"action_{selected_company}_{idx}",
                label_visibility="collapsed"
            )

            if action_choice == "✏️ แก้ไข":
                st.session_state[f"editing_item_{selected_company}_{idx}"] = True
            elif action_choice == "🗑️ ลบ":
                st.session_state["company_inventories"][selected_company] = current_inv.drop(idx).reset_index(drop=True)
                st.success(f"ลบสินค้า '{row['Item Name']}' เรียบร้อยแล้ว")
                st.rerun()

            if st.session_state.get(f"editing_item_{selected_company}_{idx}", False):
                with st.form(f"form_edit_item_{selected_company}_{idx}"):
                    st.markdown(f"**กำลังแก้ไขสินค้า:** {row['Item Name']}")
                    e_code = st.text_input("รหัสสินค้า", value=str(row["Product Code"]))
                    e_name = st.text_input("ชื่อสินค้า", value=str(row["Item Name"]))
                    e_supplier = st.text_input("ร้านค้า", value=str(row["Supplier"]))
                    e_cat = st.selectbox("หมวดหมู่สินค้า", st.session_state.categories_list, index=st.session_state.categories_list.index(row["Category"]) if row["Category"] in st.session_state.categories_list else 0)
                    e_unit = st.selectbox("หน่วยนับ", st.session_state.units_list, index=st.session_state.units_list.index(row["Unit"]) if row["Unit"] in st.session_state.units_list else 0)
                    e_price = st.number_input("ราคาล่าสุด", value=float(row["Last Price"]))
                    
                    col_sub1, col_sub2 = st.columns(2)
                    with col_sub1:
                        if st.form_submit_button("💾 บันทึกการแก้ไข"):
                            st.session_state["company_inventories"][selected_company].loc[idx, "Product Code"] = e_code
                            st.session_state["company_inventories"][selected_company].loc[idx, "Item Name"] = e_name
                            st.session_state["company_inventories"][selected_company].loc[idx, "Supplier"] = e_supplier
                            st.session_state["company_inventories"][selected_company].loc[idx, "Category"] = e_cat
                            st.session_state["company_inventories"][selected_company].loc[idx, "Unit"] = e_unit
                            st.session_state["company_inventories"][selected_company].loc[idx, "Last Price"] = e_price
                            st.session_state[f"editing_item_{selected_company}_{idx}"] = False
                            st.success("บันทึกการแก้ไขเรียบร้อยแล้ว!")
                            st.rerun()
                    with col_sub2:
                        if st.form_submit_button("❌ ยกเลิก"):
                            st.session_state[f"editing_item_{selected_company}_{idx}"] = False
                            st.rerun()

            st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
    else:
        st.info("ยังไม่มีรายการสินค้า")

# c) Add New Items
elif selected_menu == t["sub_import_excel"]:
    st.title(f"📥 เพิ่มรายการสินค้าใหม่ - {selected_company}")
    tab1, tab2, tab3, tab4 = st.tabs([
        "1. เพิ่มรายการสินค้าใหม่",
        "2. เพิ่ม/แก้ไขข้อมูลร้านค้า",
        "3. เพิ่ม/แก้ไขหน่วยนับ (Units)",
        "4. เพิ่ม/แก้ไขหมวดหมู่สินค้า (Categories)"
    ])

    with tab1:
        st.subheader("เพิ่มรายการสินค้าใหม่")
        with st.form("manual_import_form_tab"):
            existing_suppliers = current_inv["Supplier"].dropna().unique().tolist() if len(current_inv) > 0 else []
            if not existing_suppliers:
                existing_suppliers = ["CP Axtra (Makro)", "CP Axtra (Lotus)", "ร้านค้าทั่วไป"]
            
            supplier = st.selectbox("ชื่อร้านค้า (Supplier)", existing_suppliers)
            sku = st.text_input("รหัสสินค้า")
            item_name = st.text_input("ชื่อสินค้า")
            cat_manual = st.selectbox("หมวดหมู่สินค้า", st.session_state.categories_list)
            
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                unit_manual = st.selectbox("หน่วยนับ", st.session_state.units_list)
            with col_u2:
                initial_price = st.number_input("ราคาต่อหน่วย", min_value=0.0, value=0.0)
                
            vat_type = st.selectbox("ประเภทภาษี", VAT_TYPES_LIST)
            submit_manual = st.form_submit_button("💾 บันทึกเพิ่มรายการสินค้าใหม่")

            if submit_manual:
                inv = st.session_state["company_inventories"][selected_company]
                idx_match = inv.index[inv["Item Name"] == item_name]
                if not idx_match.empty:
                    idx = idx_match[0]
                    inv.loc[idx, "Supplier"] = supplier
                    inv.loc[idx, "Category"] = cat_manual
                    inv.loc[idx, "Unit"] = unit_manual
                    inv.loc[idx, "Last Price"] = initial_price
                else:
                    new_row = pd.DataFrame([{
                        "Product Code": sku,
                        "Item Name": item_name,
                        "Category": cat_manual,
                        "Unit": unit_manual,
                        "Conversion Qty": 1.0,
                        "Stock Balance": 0.0,
                        "Last Price": initial_price,
                        "Supplier": supplier,
                        "Vat Type": vat_type,
                    }])
                    st.session_state["company_inventories"][selected_company] = pd.concat(
                        [inv, new_row], ignore_index=True
                    )

                st.success("บันทึกเพิ่มรายการสินค้าใหม่สำเร็จ!")
                st.rerun()

    with tab2:
        st.subheader("ตั้งค่าข้อมูลบริษัท / สาขา (ที่อยู่ / โลโก้)")
        curr_details = st.session_state["company_details"].get(selected_company, {
            "name": selected_company, "address": "", "tax_id": "", "contact": ""
        })
        existing_logo = st.session_state["company_logos"].get(selected_company)
        if existing_logo is not None:
            st.image(existing_logo, width=150, caption="โลโก้ปัจจุบันของบริษัท")
        
        with st.form("company_info_form_in_add"):
            c_name = st.text_input("1. ชื่อบริษัท/สาขา", value=curr_details.get("name", selected_company))
            c_address = st.text_area("2. ที่อยู่", value=curr_details.get("address", ""))
            c_tax = st.text_input("3. เลขที่ผู้เสียภาษี", value=curr_details.get("tax_id", ""))
            c_contact = st.text_input("4. ข้อมูลติดต่อ / เซลล์", value=curr_details.get("contact", ""))
            
            uploaded_logo = st.file_uploader("🖼️ อัปโหลดโลโก้บริษัท (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"], key="logo_add_page")
            if st.form_submit_button("💾 บันทึกข้อมูลบริษัท"):
                st.session_state["company_details"][selected_company] = {
                    "name": c_name, "address": c_address, "tax_id": c_tax, "contact": c_contact
                }
                if uploaded_logo is not None:
                    st.session_state["company_logos"][selected_company] = uploaded_logo
                st.success("บันทึกข้อมูลบริษัทเรียบร้อยแล้ว!")
                st.rerun()

    with tab3:
        st.subheader("หน่วยนับสินค้า (Units)")
        with st.form("unit_mgmt_form"):
            new_unit = st.text_input("เพิ่มหน่วยใหม่")
            if st.form_submit_button("➕ เพิ่มหน่วยนับ"):
                if new_unit and new_unit not in st.session_state.units_list:
                    st.session_state.units_list.append(new_unit)
                    st.success(f"เพิ่มหน่วย '{new_unit}' เรียบร้อยแล้ว")
                    st.rerun()
                else:
                    st.warning("หน่วยนี้มีอยู่แล้ว หรือไม่ถูกต้อง")

        st.markdown("---")
        st.write("หน่วยนับปัจจุบัน:")
        for i, u_item in enumerate(st.session_state.units_list):
            cols = st.columns([3, 1, 1])
            cols[0].write(f"- {u_item}")
            if cols[1].button("✏️ แก้ไข", key=f"edit_unit_{i}"):
                st.session_state[f"show_edit_unit_{i}"] = not st.session_state.get(f"show_edit_unit_{i}", False)
            if cols[2].button("🗑️ ลบ", key=f"del_unit_{i}"):
                if len(st.session_state.units_list) > 1:
                    st.session_state.units_list.pop(i)
                    st.success("ลบหน่วยนับเรียบร้อยแล้ว")
                    st.rerun()
                else:
                    st.warning("ต้องมีหน่วยนับอย่างน้อย 1 รายการ")
            
            if st.session_state.get(f"show_edit_unit_{i}", False):
                with st.form(f"form_edit_unit_{i}"):
                    updated_unit_name = st.text_input("แก้ไขชื่อหน่วยนับ", value=u_item)
                    if st.form_submit_button("💾 บันทึก"):
                        if updated_unit_name and updated_unit_name not in st.session_state.units_list:
                            st.session_state.units_list[i] = updated_unit_name
                            st.session_state[f"show_edit_unit_{i}"] = False
                            st.success("แก้ไขหน่วยนับเรียบร้อยแล้ว")
                            st.rerun()
                        else:
                            st.warning("ชื่อหน่วยนับว่าง หรือซ้ำกับที่มีอยู่แล้ว")

    with tab4:
        st.subheader("หมวดหมู่สินค้า (Categories)")
        with st.form("cat_mgmt_form"):
            new_cat = st.text_input("เพิ่มหมวดหมู่ใหม่")
            if st.form_submit_button("➕ เพิ่มหมวดหมู่"):
                if new_cat and new_cat not in st.session_state.categories_list:
                    st.session_state.categories_list.append(new_cat)
                    st.success(f"เพิ่มหมวดหมู่ '{new_cat}' เรียบร้อยแล้ว")
                    st.rerun()
                else:
                    st.warning("หมวดหมู่นี้มีอยู่แล้ว หรือไม่ถูกต้อง")

        st.markdown("---")
        st.write("หมวดหมู่ปัจจุบัน:")
        for j, c_item in enumerate(st.session_state.categories_list):
            cols_c = st.columns([3, 1, 1])
            cols_c[0].write(f"- {c_item}")
            if cols_c[1].button("✏️ แก้ไข", key=f"edit_cat_{j}"):
                st.session_state[f"show_edit_cat_{j}"] = not st.session_state.get(f"show_edit_cat_{j}", False)
            if cols_c[2].button("🗑️ ลบ", key=f"del_cat_{j}"):
                if len(st.session_state.categories_list) > 1:
                    st.session_state.categories_list.pop(j)
                    st.success("ลบหมวดหมู่เรียบร้อยแล้ว")
                    st.rerun()
                else:
                    st.warning("ต้องมีหมวดหมู่อย่างน้อย 1 รายการ")
            
            if st.session_state.get(f"show_edit_cat_{j}", False):
                with st.form(f"form_edit_cat_{j}"):
                    updated_cat_name = st.text_input("แก้ไขชื่อหมวดหมู่", value=c_item)
                    if st.form_submit_button("💾 บันทึก"):
                        if updated_cat_name and updated_cat_name not in st.session_state.categories_list:
                            st.session_state.categories_list[j] = updated_cat_name
                            st.session_state[f"show_edit_cat_{j}"] = False
                            st.success("แก้ไขหมวดหมู่เรียบร้อยแล้ว")
                            st.rerun()
                        else:
                            st.warning("ชื่อหมวดหมู่ว่าง หรือซ้ำกับที่มีอยู่แล้ว")

# d) Stock In
elif selected_menu == t["sub_stock_in"]:
    st.title(f"📥 รับสินค้าเข้าสต็อก (Stock In) - {selected_company}")
    if len(current_inv) == 0:
        st.warning("ยังไม่มีรายการสินค้าในระบบ กรุณาเพิ่มรายการสินค้าก่อน")
    else:
        col_si1, col_si2, col_si3 = st.columns(3)
        with col_si1:
            si_date = st.date_input("วันที่รับสินค้า", value=datetime.today())
        with col_si2:
            existing_suppliers = current_inv["Supplier"].dropna().unique().tolist()
            si_supplier = st.selectbox("ร้านค้า / Supplier", existing_suppliers if existing_suppliers else ["CP Axtra (Makro)"])
        with col_si3:
            si_doc_no = st.text_input("เลขที่ใบส่งของ / Invoice No.")

        st.markdown("---")
        st.subheader("เลือกและเพิ่มสินค้าเข้าตะกร้ารับเข้า")
        
        si_search_query = st.text_input("🔍 พิมพ์รหัสสินค้า (Product Code) หรือ ชื่อสินค้า เพื่อดึงข้อมูลอัตโนมัติ", value="")
        
        selected_item_name = ""
        default_unit = "หน่วย"
        default_price = 0.0
        found_code = ""

        if si_search_query:
            q = str(si_search_query).strip().lower()
            res = current_inv[
                (current_inv["Product Code"].astype(str).str.strip().str.lower() == q) |
                (current_inv["Item Name"].astype(str).str.lower().str.contains(q, na=False)) |
                (current_inv["Product Code"].astype(str).str.lower().str.contains(q, na=False))
            ]
            if not res.empty:
                selected_item_name = str(res.iloc[0]["Item Name"])
                default_unit = str(res.iloc[0]["Unit"])
                default_price = float(res.iloc[0]["Last Price"])
                found_code = str(res.iloc[0]["Product Code"])

        with st.form("form_add_stock_in_item"):
            if si_search_query:
                if selected_item_name:
                    st.success(f"✅ พบสินค้า [รหัส: {found_code}] -> **{selected_item_name}**")
                else:
                    st.error("❌ ไม่พบสินค้าที่ตรงกับรหัสหรือชื่อนี้")
            else:
                st.info("💡 กรุณาพิมพ์รหัสสินค้าหรือชื่อสินค้าในช่องด้านบนเพื่อค้นหา")

            col_sq1, col_sq2, col_sq3 = st.columns(3)
            with col_sq1:
                si_qty = st.number_input("จำนวนที่รับเข้า", min_value=0.1, value=1.0)
            with col_sq2:
                unit_idx = st.session_state.units_list.index(default_unit) if default_unit in st.session_state.units_list else 0
                si_unit = st.selectbox("หน่วยนับ (ดึงอัตโนมัติ)", st.session_state.units_list, index=unit_idx)
            with col_sq3:
                si_price = st.number_input("ราคาซื้อต่อหน่วย (ดึงอัตโนมัติ)", min_value=0.0, value=default_price)

            add_to_si_cart = st.form_submit_button("➕ เพิ่มรายการนี้เข้าตะกร้ารับสินค้า")
            if add_to_si_cart:
                if selected_item_name:
                    st.session_state["temp_stock_in_cart"].append({
                        "Item Name": selected_item_name,
                        "Quantity": si_qty,
                        "Unit": si_unit,
                        "Price": si_price,
                        "Total": si_qty * si_price
                    })
                    st.success(f"เพิ่ม '{selected_item_name}' ลงในรายการรับเข้าแล้ว")
                    st.rerun()
                else:
                    st.error("กรุณาระบุรหัสหรือชื่อสินค้าให้ถูกต้องก่อนเพิ่มลงตะกร้า")

        if len(st.session_state["temp_stock_in_cart"]) > 0:
            st.markdown("#### 🛒 รายการสินค้าที่รอรับเข้าสต็อก")
            cart_df = pd.DataFrame(st.session_state["temp_stock_in_cart"])
            st.dataframe(cart_df, use_container_width=True)
            
            total_si_amount = cart_df["Total"].sum()
            st.markdown(f"### 💵 มูลค่ารับเข้ารวมทั้งหมด: **{total_si_amount:,.2f} THB**")

            col_sb1, col_sb2 = st.columns(2)
            with col_sb1:
                if st.button("🗑️ ล้างตะกร้ารับสินค้า"):
                    st.session_state["temp_stock_in_cart"] = []
                    st.rerun()
            with col_sb2:
                if st.button("💾 บันทึกรับเข้าสต็อกจริง (Update Stock)"):
                    inv = st.session_state["company_inventories"][selected_company]
                    for item in st.session_state["temp_stock_in_cart"]:
                        i_name = item["Item Name"]
                        i_qty = item["Quantity"]
                        i_unit = item["Unit"]
                        i_price = item["Price"]
                        
                        idx_match = inv.index[inv["Item Name"] == i_name]
                        if not idx_match.empty:
                            idx = idx_match[0]
                            inv.loc[idx, "Stock Balance"] += i_qty
                            inv.loc[idx, "Last Price"] = i_price

                        new_trans = pd.DataFrame([{
                            "Date": str(si_date),
                            "Branch": selected_company,
                            "Type": "รับเข้า (Stock In)",
                            "Item Name": i_name,
                            "Quantity": i_qty,
                            "Unit": i_unit,
                            "Note": f"Invoice: {si_doc_no} / Supplier: {si_supplier}"
                        }])
                        st.session_state["transaction_history"] = pd.concat([st.session_state["transaction_history"], new_trans], ignore_index=True)

                    st.session_state["temp_stock_in_cart"] = []
                    st.success("บันทึกรับสินค้าเข้าสต็อกและปรับปรุงยอดคงเหลือสำเร็จ!")
                    st.rerun()

# e) Stock Out
elif selected_menu == t["sub_stock_out"]:
    st.title(f"📤 เบิกสินค้าออกจากสต็อก (Stock Out) - {selected_company}")
    if len(current_inv) == 0:
        st.warning("ยังไม่มีรายการสินค้าในระบบ")
    else:
        with st.form("stock_out_form"):
            so_date = st.date_input("วันที่เบิกสินค้า", value=datetime.today())
            so_item = st.selectbox("เลือกรายการสินค้า", current_inv["Item Name"].tolist())
            
            default_unit = "หน่วย"
            current_bal = 0.0
            matched_item = current_inv[current_inv["Item Name"] == so_item]
            if not matched_item.empty:
                default_unit = str(matched_item.iloc[0]["Unit"])
                current_bal = float(matched_item.iloc[0]["Stock Balance"])

            st.info(f"สต็อกคงเหลือปัจจุบัน: **{current_bal} {default_unit}**")

            so_qty = st.number_input("จำนวนที่ต้องการเบิกออก", min_value=0.1, value=1.0)
            so_unit = st.selectbox("หน่วยนับ", st.session_state.units_list, index=st.session_state.units_list.index(default_unit) if default_unit in st.session_state.units_list else 0)
            so_note = st.text_input("หมายเหตุ / ผู้เบิก / แผนกที่ใช้")

            submit_so = st.form_submit_button("💾 บันทึกเบิกสินค้าออก")
            if submit_so:
                if so_qty > current_bal:
                    st.error("จำนวนที่เบิกมากกว่าสต็อกคงเหลือในระบบ!")
                else:
                    inv = st.session_state["company_inventories"][selected_company]
                    idx = inv.index[inv["Item Name"] == so_item][0]
                    inv.loc[idx, "Stock Balance"] -= so_qty
                    
                    new_trans = pd.DataFrame([{
                        "Date": str(so_date),
                        "Branch": selected_company,
                        "Type": "เบิกออก (Stock Out)",
                        "Item Name": so_item,
                        "Quantity": so_qty,
                        "Unit": so_unit,
                        "Note": so_note
                    }])
                    st.session_state["transaction_history"] = pd.concat([st.session_state["transaction_history"], new_trans], ignore_index=True)
                    st.success(f"เบิกสินค้า '{so_item}' จำนวน {so_qty} {so_unit} เรียบร้อยแล้ว!")
                    st.rerun()

# f) PR / PO workflow
elif selected_menu == t["sub_pr_po"]:
    st.title(f"📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO) - {selected_company}")
    pr_tab1, pr_tab2 = st.tabs(["📄 1. สร้างและติดตามใบขอซื้อ (PR)", "📦 2. ออกใบสั่งซื้อ (PO)"])

    with pr_tab1:
        st.subheader("สร้างใบขอซื้อสินค้า (PR)")

        if "temp_pr_cart" not in st.session_state:
            st.session_state["temp_pr_cart"] = []

        col_pr1, col_pr2, col_pr3 = st.columns(3)
        with col_pr1:
            pr_date = st.date_input("วันที่ขอซื้อ", value=datetime.today(), key="pr_date_input")
        with col_pr2:
            existing_suppliers = current_inv["Supplier"].unique().tolist() if len(current_inv) > 0 else ["CP Axtra (Makro)"]
            pr_supplier = st.selectbox("ร้านค้า / Supplier สำหรับขอซื้อ", existing_suppliers, key="pr_sup_input")
        with col_pr3:
            pr_requester = st.text_input("ผู้ขอซื้อ", value=user_info["Name"], key="pr_req_input")

        st.markdown("---")
        st.write("### เพิ่มรายการสินค้าในใบขอซื้อ")
        inv_for_pr = current_inv[current_inv["Supplier"] == pr_supplier] if len(current_inv) > 0 else pd.DataFrame()
        if len(inv_for_pr) == 0:
            inv_for_pr = current_inv.copy()

        with st.form("form_add_pr_item"):
            pr_item_name = st.selectbox("เลือกรายการสินค้า", inv_for_pr["Item Name"].tolist() if len(inv_for_pr) > 0 else [])
            
            default_pr_unit = "หน่วย"
            if pr_item_name and len(current_inv) > 0:
                m_u = current_inv[current_inv["Item Name"] == pr_item_name]
                if not m_u.empty and "Unit" in m_u.columns:
                    default_pr_unit = str(m_u.iloc[0]["Unit"])

            col_pi1, col_pi2 = st.columns(2)
            with col_pi1:
                pr_qty = st.number_input("จำนวนที่ขอซื้อ", min_value=0.1, value=1.0)
            with col_pi2:
                pr_unit = st.selectbox("หน่วยนับ", st.session_state.units_list, index=st.session_state.units_list.index(default_pr_unit) if default_pr_unit in st.session_state.units_list else 0, key="pr_unit_select")

            add_to_pr_cart = st.form_submit_button("➕ เพิ่มรายการนี้เข้าตะกร้า PR")
            if add_to_pr_cart and pr_item_name:
                item_price = 0.0
                if len(current_inv) > 0:
                    matched_p = current_inv[current_inv["Item Name"] == pr_item_name]
                    if not matched_p.empty:
                        item_price = float(matched_p.iloc[0]["Last Price"])

                st.session_state["temp_pr_cart"].append({
                    "Item Name": pr_item_name,
                    "Quantity": pr_qty,
                    "Unit": pr_unit,
                    "Price": item_price,
                    "Total": pr_qty * item_price
                })
                st.success(f"เพิ่ม {pr_item_name} ลงในตะกร้า PR แล้ว")

        if len(st.session_state["temp_pr_cart"]) > 0:
            st.markdown("#### รายการสินค้าในตะกร้า PR ปัจจุบัน")
            temp_df_cart = pd.DataFrame(st.session_state["temp_pr_cart"])
            st.dataframe(temp_df_cart, use_container_width=True)
            
            total_cart_amount = temp_df_cart["Total"].sum()
            st.markdown(f"### 💵 ยอดราคาสั่งซื้อรวมทั้งหมด: **{total_cart_amount:,.2f} THB**")

            col_pr_b1, col_pr_b2 = st.columns(2)
            with col_pr_b1:
                if st.button("🗑️ ล้างตะกร้า PR"):
                    st.session_state["temp_pr_cart"] = []
                    st.rerun()
            with col_pr_b2:
                if st.button("💾 บันทึกและส่งใบขอซื้อ (PR) ทั้งหมด"):
                    new_pr_id = f"PR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    new_pr_row = pd.DataFrame([{
                        "PR_ID": new_pr_id,
                        "Date": str(pr_date),
                        "Supplier": pr_supplier,
                        "Branch": selected_company,
                        "Status": "รอการอนุมัติ",
                        "Requester": pr_requester,
                        "Items_JSON": str(st.session_state["temp_pr_cart"]),
                        "Total_Amount": total_cart_amount
                    }])
                    st.session_state["purchase_requests"] = pd.concat([st.session_state["purchase_requests"], new_pr_row], ignore_index=True)
                    st.session_state["temp_pr_cart"] = []
                    st.success(f"บันทึกใบขอซื้อเลขที่ {new_pr_id} เรียบร้อยแล้ว!")
                    st.rerun()

        st.markdown("---")
        st.subheader("ประวัติและสถานะใบขอซื้อทั้งหมด")

        if "view_pr_doc_id" not in st.session_state:
            st.session_state["view_pr_doc_id"] = None

        if st.session_state["view_pr_doc_id"] is not None:
            doc_id = st.session_state["view_pr_doc_id"]
            doc_rows = st.session_state["purchase_requests"][st.session_state["purchase_requests"]["PR_ID"] == doc_id]
            
            if not doc_rows.empty:
                d_row = doc_rows.iloc[0]
                st.markdown(f"""
                <div style="border: 2px solid #ccc; padding: 20px; border-radius: 10px; background-color: #f9f9f9; color: #333;">
                    <h2 style="text-align: center; margin-bottom: 0;">ใบขอซื้อสินค้า (PURCHASE REQUEST - PR)</h2>
                    <p style="text-align: center; color: gray;">{d_row['Branch']}</p>
                    <hr>
                    <p><b>เลขที่เอกสาร (PR ID):</b> {d_row['PR_ID']}</p>
                    <p><b>วันที่ขอซื้อ:</b> {d_row['Date']}</p>
                    <p><b>ร้านค้า / Supplier:</b> {d_row['Supplier']}</p>
                    <p><b>ผู้ขอซื้อ:</b> {d_row['Requester']}</p>
                    <p><b>สถานะ:</b> {d_row['Status']}</p>
                    <br>
                    <h4>รายการสินค้า:</h4>
                """, unsafe_allow_html=True)

                import ast
                try:
                    items_list = ast.literal_eval(d_row["Items_JSON"])
                    st.dataframe(pd.DataFrame(items_list), use_container_width=True)
                except:
                    st.write(d_row["Items_JSON"])

                total_amt = d_row.get("Total_Amount", 0.0)
                st.markdown(f"<h3>ยอดราคาสั่งซื้อรวม: {total_amt:,.2f} THB</h3>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                if st.button("⬅️ ปิดเอกสารและกลับสู่ตารางหลัก"):
                    st.session_state["view_pr_doc_id"] = None
                    st.rerun()
                st.markdown("---")

        if len(st.session_state["purchase_requests"]) > 0:
            for idx, row in st.session_state["purchase_requests"].iterrows():
                cols_pr = st.columns([1.5, 1.2, 1.8, 2, 1.2, 1.8, 2])
                
                if cols_pr[0].button(str(row["PR_ID"]), key=f"btn_view_{row['PR_ID']}_{idx}"):
                    st.session_state["view_pr_doc_id"] = row["PR_ID"]
                    st.rerun()

                cols_pr[1].write(str(row["Date"]))
                cols_pr[2].write(str(row["Supplier"]))
                cols_pr[3].write(str(row["Branch"]))
                
                tot_val = row.get("Total_Amount", 0.0)
                cols_pr[4].write(f"{tot_val:,.2f} ฿")
                
                cols_pr[5].write(str(row["Requester"]))
                
                current_status = str(row["Status"])
                is_locked = ("อนุมัติ" in current_status and "รอ" not in current_status) or ("ปฏิเสธ" in current_status)

                if is_locked:
                    if "อนุมัติ" in current_status and "รอ" not in current_status:
                        cols_pr[6].markdown("🟢 **อนุมัติแล้ว (ล็อก)**")
                    else:
                        cols_pr[6].markdown("🔴 **ปฏิเสธแล้ว (ล็อก)**")
                else:
                    status_options = ["รอการอนุมัติ", "อนุมัติ", "ปฏิเสธ"]
                    new_status_choice = cols_pr[6].selectbox(
                        "สถานะ",
                        status_options,
                        index=0,
                        key=f"status_dropdown_{idx}",
                        label_visibility="collapsed"
                    )

                    if new_status_choice != current_status:
                        st.session_state["purchase_requests"].loc[idx, "Status"] = new_status_choice
                        if new_status_choice == "อนุมัติ":
                            new_po_id = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                            new_po_row = pd.DataFrame([{
                                "PO_ID": new_po_id,
                                "PR_ID": row["PR_ID"],
                                "Supplier": row["Supplier"],
                                "Branch": row["Branch"],
                                "Date": str(datetime.today().date())
                            }])
                            st.session_state["purchase_orders"] = pd.concat([st.session_state["purchase_orders"], new_po_row], ignore_index=True)
                        st.rerun()

                st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
        else:
            st.info("ยังไม่มีใบขอซื้อในระบบ")

    with pr_tab2:
        st.subheader("ออกใบสั่งซื้อ (PO) จาก PR ที่อนุมัติแล้ว")
        approved_prs = st.session_state["purchase_requests"][st.session_state["purchase_requests"]["Status"] == "อนุมัติ"]
        if len(approved_prs) > 0:
            st.dataframe(approved_prs, use_container_width=True)
        else:
            st.info("ยังไม่มีใบขอซื้อที่ได้รับการอนุมัติในขณะนี้")

        st.markdown("---")
        st.subheader("ประวัติใบสั่งซื้อ (PO)")
        if len(st.session_state["purchase_orders"]) > 0:
            st.dataframe(st.session_state["purchase_orders"], use_container_width=True)
        else:
            st.info("ยังไม่มีใบสั่งซื้อในระบบ")

# g) History
elif selected_menu == t["sub_history"]:
    st.title(f"⏱️ ประวัติการทำรายการ - {selected_company}")
    if len(st.session_state["transaction_history"]) > 0:
        st.dataframe(st.session_state["transaction_history"], use_container_width=True)
    else:
        st.info("ยังไม่มีประวัติการทำรายการรับ-เบิกสินค้า")

# h) Report
elif selected_menu == t["sub_report"]:
    st.title(f"📈 รายการสรุปสต็อก & นับสต็อก - {selected_company}")
    if len(current_inv) > 0:
        st.dataframe(current_inv, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลในระบบสต็อก")

# i) Settings
elif selected_menu == t["sub_settings"]:
    st.title(f"⚙️ ตั้งค่าข้อมูลบริษัทและแอดมิน - {selected_company}")
    st.info("ตั้งค่าระบบผู้ใช้งานและข้อมูลองค์กร")
