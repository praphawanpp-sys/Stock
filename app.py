import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO) - Daddy Deli",
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

if "company_details" not in st.session_state:
    st.session_state["company_details"] = {
        "Daddy Deli": {
            "name": "บริษัท เดอะ เล็ค ล็อดจ์ กรุ๊ป จำกัด ( สำนักงานใหญ่ )",
            "name_en": "The Lake Lodge Group Co.,Ltd. ( Head Office )",
            "address": "No.17 Moo.7 Hin Lek Fai Subdistrict, Hua Hin District, Prachuap Khiri Khan Province 77110",
            "tax_id": "0775565003672",
            "contact": "-"
        },
        "Daddy Deli Beach House": {
            "name": "บริษัท แดดดี้ส์ เดลี่ บีชเฮ้าส์ จำกัด ( สำนักงานใหญ่ )",
            "name_en": "Daddy Deli Beach House Co.,Ltd. ( Head Office )",
            "address": "No.19 Soi Moo Ban Khaotao, Nong Kae, Hua Hin, Prachuap Khiri Khan Province 77110",
            "tax_id": "0775569000872",
            "contact": "-"
        },
        "Daddy Deli Pattaya Group": {
            "name": "บริษัท แดดดี้ส์ เดลี่ พัทยา กรุ๊ป จำกัด ( สำนักงานใหญ่ )",
            "name_en": "Daddy Deli Pattaya Group Co.,Ltd. ( Head Office )",
            "address": "No.391/116 Moo 10, Nong Prue Subdistrict, Bang Lamung District, Chonburi Province 20150",
            "tax_id": "0205569016935",
            "contact": "-"
        },
        "Harvest Cafe": {
            "name": "บริษัท เดอะ เล็ค ล็อดจ์ กรุ๊ป จำกัด ( สาขา 0001 )",
            "name_en": "The Lake Lodge Group Co.,Ltd. ( Branch 0001 )",
            "address": "779 Village No.7 Hin Lek Fai Subdistrict, Hua Hin District, Prachuap Khiri Khan Province 77110",
            "tax_id": "0775565003672",
            "contact": "-"
        },
        "Taboo By Daddy Deli": {
            "name": "บริษัท เดอะ เล็ค ล็อดจ์ กรุ๊ป จำกัด ( สาขา 0002 )",
            "name_en": "The Lake Lodge Group Co.,Ltd. ( Branch 0002 )",
            "address": "No.10/238 Soi Moo Ban Samor Phrong, Hua Hin District, Prachuap Khiri Khan Province 77110",
            "tax_id": "0775565003672",
            "contact": "-"
        },
        "Harvest Bakery And Restaurant": {
            "name": "บริษัท ฮาร์เวสต์ เบเกอรี่ แอนด์ เรสเตอรองต์ จำกัด ( สำนักงานใหญ่ )",
            "name_en": "Harvest Bakery And Restaurant Co.,Ltd. ( Head Office )",
            "address": "779 Village No.7 Hin Lek Fai Subdistrict, Hua Hin District, Prachuap Khiri Khan Province 77110",
            "tax_id": "0775569002727",
            "contact": "-"
        }
    }

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
# 2. DICTIONARY TRANSLATIONS & MAPPINGS (ระบบแปลภาษาและคำศัพท์)
# ----------------------------------------------------
item_translations = {
    "นมจืด 2 ลิตร": "Fresh Milk 2 Liters"
}

category_translations = {
    "นม / Milk": "Milk",
    "เบเกอรี่ / Bakery": "Bakery",
    "เครื่องดื่ม / Beverage": "Beverage",
    "วัตถุดิบอาหาร / Ingredients": "Food Ingredients"
}

def translate_item_name(name, lang):
    if lang == "English":
        return item_translations.get(name, name)
    return name

def translate_category(cat, lang):
    if lang == "English":
        return category_translations.get(cat, cat)
    return cat

texts = {
    "ไทย (Thai)": {
        "user_title": "👤 ผู้ใช้งานปัจจุบัน (Current User)",
        "company_title": "🏢 เลือกบริษัท / สาขา",
        "menu_title": "⚡ เมนูหลัก",
        "m1": "📊 แดชบอร์ดภาพรวม",
        "m2": "📦 การจัดการรายการสินค้า",
        "m3": "📥 เพิ่มรายการสินค้าใหม่",
        "m4": "📥 รับสินค้า (Stock In)",
        "m5": "📤 เบิกสินค้า (Stock Out)",
        "m6": "📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)",
        "m7": "⏱️ ประวัติการทำรายการ",
        "m8": "📈 รายการสรุปสต็อก & นับสต็อก",
        "m9": "⚙️ ตั้งค่าข้อมูลบริษัทและแอดมิน",
        "add_item_title": "เพิ่มรายการสินค้าใหม่",
        "tab_add": "1. เพิ่มรายการสินค้าใหม่",
        "tab_store": "2. เพิ่ม/แก้ไขข้อมูลร้านค้า",
        "tab_unit": "3. เพิ่ม/แก้ไขหน่วยนับ (Units)",
        "tab_cat": "4. เพิ่ม/แก้ไขหมวดหมู่สินค้า (Categories)",
        "lbl_supplier": "ชื่อร้านค้า (Supplier)",
        "lbl_sku": "รหัสสินค้า",
        "lbl_item_name": "ชื่อสินค้า",
        "lbl_category": "หมวดหมู่สินค้า",
        "lbl_unit": "หน่วยนับ",
        "lbl_price": "ราคาต่อหน่วย",
        "lbl_vat": "ประเภทภาษี",
        "btn_save": "💾 บันทึกเพิ่มรายการสินค้าใหม่",
        "err_fill": "⚠️ กรุณากรอกรหัสสินค้าและชื่อสินค้าให้ครบถ้วนก่อนบันทึก",
        "success_update": "🎉 อัปเดตข้อมูลสินค้าเรียบร้อยแล้ว!",
        "success_save": "✨ บันทึกเพิ่มรายการสินค้าใหม่สำเร็จแล้ว!"
    },
    "English": {
        "user_title": "👤 Current User",
        "company_title": "🏢 Select Company / Branch",
        "menu_title": "⚡ Main Menu",
        "m1": "📊 Dashboard",
        "m2": "📦 Inventory Management",
        "m3": "📥 Add New Items",
        "m4": "📥 Stock In",
        "m5": "📤 Stock Out",
        "m6": "📝 PR & PO System",
        "m7": "⏱️ Transaction History",
        "m8": "📈 Stock Summary & Count",
        "m9": "⚙️ Settings",
        "add_item_title": "Add New Items",
        "tab_add": "1. Add New Items",
        "tab_store": "2. Store Info Setup",
        "tab_unit": "3. Manage Units",
        "tab_cat": "4. Manage Categories",
        "lbl_supplier": "Supplier Name",
        "lbl_sku": "Product Code",
        "lbl_item_name": "Item Name",
        "lbl_category": "Category",
        "lbl_unit": "Unit",
        "lbl_price": "Price per Unit",
        "lbl_vat": "VAT Type",
        "btn_save": "💾 Save New Item",
        "err_fill": "⚠️ Please fill in Product Code and Item Name completely.",
        "success_update": "🎉 Item data updated successfully!",
        "success_save": "✨ New item saved successfully!"
    }
}

# ----------------------------------------------------
# 3. SIDEBAR CONFIGURATION
# ----------------------------------------------------
st.sidebar.markdown("### 🌐 ภาษา / Language")
lang = st.sidebar.selectbox("Language", ["ไทย (Thai)", "English"], label_visibility="collapsed")
t_ui = texts[lang]

st.sidebar.markdown(f"### {t_ui['user_title']}")
current_user = st.sidebar.selectbox("User", ["owner_master", "staff_procurement"], label_visibility="collapsed")
user_info = {"Name": "Mr. Owner" if current_user == "owner_master" else "Staff PR", "Role": "Owner" if current_user == "owner_master" else "Staff"}

st.sidebar.markdown(f"### {t_ui['company_title']}")
selected_company = st.sidebar.selectbox("Company", st.session_state.companies_list, label_visibility="collapsed")

curr_comp_details = st.session_state["company_details"].get(selected_company, {})
st.sidebar.caption(f"Address: {curr_comp_details.get('address', '-')}\n\nTax ID: {curr_comp_details.get('tax_id', '-')}\n\nContact: {curr_comp_details.get('contact', '-')}")
st.sidebar.info(f"**{user_info['Name']}**\n\nRole: {user_info['Role']}")

# ----------------------------------------------------
# 4. MAIN NAVIGATION MENU
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown(f"### {t_ui['menu_title']}")

menu_options = [
    t_ui["m1"], t_ui["m2"], t_ui["m3"], t_ui["m4"], 
    t_ui["m5"], t_ui["m6"], t_ui["m7"], t_ui["m8"], t_ui["m9"]
]

selected_menu = st.sidebar.radio(
    "Menu",
    menu_options,
    label_visibility="collapsed"
)

if selected_company not in st.session_state["company_inventories"]:
    st.session_state["company_inventories"][selected_company] = pd.DataFrame(columns=[
        "Product Code", "Item Name", "Category", "Unit", "Conversion Qty", "Stock Balance", "Last Price", "Supplier", "Vat Type"
    ])
current_inv = st.session_state["company_inventories"][selected_company]

# แปลงภาษาของข้อมูลใน DataFrame ตามภาษาที่เลือกแสดงผล
display_inv = current_inv.copy()
if len(display_inv) > 0 and lang == "English":
    display_inv["Item Name"] = display_inv["Item Name"].apply(lambda x: translate_item_name(x, lang))
    display_inv["Category"] = display_inv["Category"].apply(lambda x: translate_category(x, lang))

# ----------------------------------------------------
# 5. ROUTING LOGIC
# ----------------------------------------------------

# เมนูที่ 1: แดชบอร์ดภาพรวม
if selected_menu == t_ui["m1"]:
    st.title(f"{t_ui['m1']} - {selected_company}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items" if lang == "English" else "จำนวนรายการสินค้าทั้งหมด", f"{len(display_inv)}")
    col2.metric("Total PRs" if lang == "English" else "ใบขอซื้อ (PR) ทั้งหมด", f"{len(st.session_state['purchase_requests'])}")
    col3.metric("Total POs" if lang == "English" else "ใบสั่งซื้อ (PO) ทั้งหมด", f"{len(st.session_state['purchase_orders'])}")
    st.markdown("---")
    st.subheader("Current Inventory" if lang == "English" else "รายการสินค้าในระบบปัจจุบัน")
    if len(display_inv) > 0:
        st.dataframe(display_inv, use_container_width=True)
    else:
        st.info("No items in this branch." if lang == "English" else "ยังไม่มีข้อมูลสินค้าในระบบสาขานี้")

# เมนูที่ 2: การจัดการรายการสินค้า
elif selected_menu == t_ui["m2"]:
    st.title(f"{t_ui['m2']} - {selected_company}")
    st.caption("Summary of all items in this branch." if lang == "English" else "สรุปสินค้าทั้งหมดของบริษัท/สาขานั้นๆ ว่ามีสินค้าอะไรบ้าง")
    
    if len(display_inv) > 0:
        st.markdown("#### 🔍 Search Products" if lang == "English" else "#### 🔍 ค้นหาข้อมูลสินค้า")
        scol1, scol2, scol3 = st.columns(3)
        with scol1:
            search_supplier = st.text_input("Supplier" if lang == "English" else "ค้นหาตามชื่อร้านค้า (Supplier)")
        with scol2:
            search_code = st.text_input("Product Code" if lang == "English" else "ค้นหาตามรหัสสินค้า (Product Code)")
        with scol3:
            cat_options = ["All" if lang == "English" else "ทั้งหมด"] + display_inv["Category"].dropna().unique().tolist()
            search_category = st.selectbox("Category" if lang == "English" else "ค้นหาตามหมวดหมู่ (Category)", cat_options)

        filtered_df = display_inv.copy()
        if search_supplier:
            filtered_df = filtered_df[filtered_df["Supplier"].astype(str).str.contains(search_supplier, case=False, na=False)]
        if search_code:
            filtered_df = filtered_df[filtered_df["Product Code"].astype(str).str.contains(search_code, case=False, na=False)]
        if search_category not in ["All", "ทั้งหมด"]:
            filtered_df = filtered_df[filtered_df["Category"] == search_category]

        st.markdown("---")
        st.subheader("Product List & Management" if lang == "English" else "รายชื่อสินค้าในระบบและการจัดการ")

        for idx, row in filtered_df.iterrows():
            cols = st.columns([2.2, 1.2, 1.2, 1.2, 0.9, 0.9, 0.9, 1.3])
            cols[0].write(f"**{row['Item Name']}**")
            cols[1].write(f"Code: {row['Product Code']}" if lang == "English" else f"รหัส: {row['Product Code']}")
            cols[2].write(f"Sup: {row['Supplier']}" if lang == "English" else f"ร้าน: {row['Supplier']}")
            cols[3].write(f"Cat: {row['Category']}" if lang == "English" else f"หมวด: {row['Category']}")
            cols[4].write(f"Bal: {row['Stock Balance']}" if lang == "English" else f"คงเหลือ: {row['Stock Balance']}")
            cols[5].write(f"Unit: {row['Unit']}" if lang == "English" else f"หน่วย: {row['Unit']}")
            cols[6].write(f"{row['Last Price']} ฿")

            action_choice = cols[7].selectbox(
                "Action" if lang == "English" else "จัดการ", 
                ["Select" if lang == "English" else "เลือก", "✏️ Edit" if lang == "English" else "✏️ แก้ไข", "🗑️ Delete" if lang == "English" else "🗑️ ลบ"], 
                key=f"action_{selected_company}_{idx}",
                label_visibility="collapsed"
            )

            if action_choice in ["✏️ Edit", "✏️ แก้ไข"]:
                st.session_state[f"editing_item_{selected_company}_{idx}"] = True
            elif action_choice in ["🗑️ Delete", "🗑️ ลบ"]:
                st.session_state["company_inventories"][selected_company] = current_inv.drop(idx).reset_index(drop=True)
                st.success(f"Deleted '{row['Item Name']}'" if lang == "English" else f"ลบสินค้า '{row['Item Name']}' เรียบร้อยแล้ว")
                st.rerun()

            if st.session_state.get(f"editing_item_{selected_company}_{idx}", False):
                with st.form(f"form_edit_item_{selected_company}_{idx}"):
                    st.markdown(f"**Editing:** {row['Item Name']}" if lang == "English" else f"**กำลังแก้ไขสินค้า:** {row['Item Name']}")
                    e_code = st.text_input("Product Code", value=str(row["Product Code"]))
                    e_name = st.text_input("Item Name", value=str(row["Item Name"]))
                    e_supplier = st.text_input("Supplier", value=str(row["Supplier"]))
                    e_cat = st.selectbox("Category", st.session_state.categories_list, index=st.session_state.categories_list.index(current_inv.loc[idx, "Category"]) if current_inv.loc[idx, "Category"] in st.session_state.categories_list else 0)
                    e_unit = st.selectbox("Unit", st.session_state.units_list, index=st.session_state.units_list.index(current_inv.loc[idx, "Unit"]) if current_inv.loc[idx, "Unit"] in st.session_state.units_list else 0)
                    e_price = st.number_input("Last Price", value=float(row["Last Price"]))
                    
                    col_sub1, col_sub2 = st.columns(2)
                    with col_sub1:
                        if st.form_submit_button("💾 Save Changes" if lang == "English" else "💾 บันทึกการแก้ไข"):
                            st.session_state["company_inventories"][selected_company].loc[idx, "Product Code"] = e_code
                            st.session_state["company_inventories"][selected_company].loc[idx, "Item Name"] = e_name
                            st.session_state["company_inventories"][selected_company].loc[idx, "Supplier"] = e_supplier
                            st.session_state["company_inventories"][selected_company].loc[idx, "Category"] = e_cat
                            st.session_state["company_inventories"][selected_company].loc[idx, "Unit"] = e_unit
                            st.session_state["company_inventories"][selected_company].loc[idx, "Last Price"] = e_price
                            st.session_state[f"editing_item_{selected_company}_{idx}"] = False
                            st.success("Saved successfully!" if lang == "English" else "บันทึกการแก้ไขเรียบร้อยแล้ว!")
                            st.rerun()
                    with col_sub2:
                        if st.form_submit_button("❌ Cancel" if lang == "English" else "❌ ยกเลิก"):
                            st.session_state[f"editing_item_{selected_company}_{idx}"] = False
                            st.rerun()

            st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
    else:
        st.info("No items available." if lang == "English" else "ยังไม่มีรายการสินค้า")

# เมนูที่ 3: เพิ่มรายการสินค้าใหม่
elif selected_menu == t_ui["m3"]:
    st.title(f"{t_ui['m3']} - {selected_company}")
    tab1, tab2, tab3, tab4 = st.tabs([
        t_ui["tab_add"], t_ui["tab_store"], t_ui["tab_unit"], t_ui["tab_cat"]
    ])

    with tab1:
        st.subheader(t_ui["add_item_title"])
        with st.form("manual_import_form_tab"):
            existing_suppliers = current_inv["Supplier"].dropna().unique().tolist() if len(current_inv) > 0 else []
            if not existing_suppliers:
                existing_suppliers = ["CP Axtra (Makro)", "CP Axtra (Lotus)", "General Store"]
            
            supplier = st.selectbox(t_ui["lbl_supplier"], existing_suppliers)
            sku = st.text_input(t_ui["lbl_sku"])
            item_name = st.text_input(t_ui["lbl_item_name"])
            cat_manual = st.selectbox(t_ui["lbl_category"], st.session_state.categories_list)
            
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                unit_manual = st.selectbox(t_ui["lbl_unit"], st.session_state.units_list)
            with col_u2:
                initial_price = st.number_input(t_ui["lbl_price"], min_value=0.0, value=0.0)
                
            vat_type = st.selectbox(t_ui["lbl_vat"], VAT_TYPES_LIST)
            submit_manual = st.form_submit_button(t_ui["btn_save"])

            if submit_manual:
                if not sku.strip() or not item_name.strip():
                    st.error(t_ui["err_fill"])
                else:
                    inv = st.session_state["company_inventories"][selected_company]
                    idx_match = inv.index[inv["Item Name"] == item_name]
                    if not idx_match.empty:
                        idx = idx_match[0]
                        inv.loc[idx, "Supplier"] = supplier
                        inv.loc[idx, "Category"] = cat_manual
                        inv.loc[idx, "Unit"] = unit_manual
                        inv.loc[idx, "Last Price"] = initial_price
                        st.success(t_ui["success_update"])
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
                        st.success(t_ui["success_save"])

    with tab2:
        st.subheader("Store Info" if lang == "English" else "ตั้งค่าข้อมูลบริษัท / สาขา (ที่อยู่ / โลโก้)")
        curr_details = st.session_state["company_details"].get(selected_company, {
            "name": selected_company, "address": "", "tax_id": "", "contact": ""
        })
        existing_logo = st.session_state["company_logos"].get(selected_company)
        if existing_logo is not None:
            st.image(existing_logo, width=150, caption="Company Logo" if lang == "English" else "โลโก้ปัจจุบันของบริษัท")
        
        with st.form("company_info_form_in_add"):
            c_name = st.text_input("Company Name" if lang == "English" else "1. ชื่อบริษัท/สาขา", value=curr_details.get("name", selected_company))
            c_address = st.text_area("Address" if lang == "English" else "2. ที่อยู่", value=curr_details.get("address", ""))
            c_tax = st.text_input("Tax ID" if lang == "English" else "3. เลขที่ผู้เสียภาษี", value=curr_details.get("tax_id", ""))
            c_contact = st.text_input("Contact" if lang == "English" else "4. ข้อมูลติดต่อ / เซลล์", value=curr_details.get("contact", ""))
            
            uploaded_logo = st.file_uploader("Upload Logo", type=["png", "jpg", "jpeg"], key="logo_add_page")
            if st.form_submit_button("Save Store Info" if lang == "English" else "💾 บันทึกข้อมูลบริษัท"):
                st.session_state["company_details"][selected_company] = {
                    "name": c_name, "address": c_address, "tax_id": c_tax, "contact": c_contact
                }
                if uploaded_logo is not None:
                    st.session_state["company_logos"][selected_company] = uploaded_logo
                st.success("Saved!" if lang == "English" else "บันทึกข้อมูลบริษัทเรียบร้อยแล้ว!")
                st.rerun()

    with tab3:
        st.subheader("Units Management" if lang == "English" else "หน่วยนับสินค้า (Units)")
        with st.form("unit_mgmt_form"):
            new_unit = st.text_input("New Unit" if lang == "English" else "เพิ่มหน่วยใหม่")
            if st.form_submit_button("Add Unit" if lang == "English" else "➕ เพิ่มหน่วยนับ"):
                if new_unit and new_unit not in st.session_state.units_list:
                    st.session_state.units_list.append(new_unit)
                    st.success("Added unit successfully.")
                    st.rerun()
                else:
                    st.warning("Unit already exists or invalid.")

    with tab4:
        st.subheader("Categories Management" if lang == "English" else "หมวดหมู่สินค้า (Categories)")
        with st.form("cat_mgmt_form"):
            new_cat = st.text_input("New Category" if lang == "English" else "เพิ่มหมวดหมู่ใหม่")
            if st.form_submit_button("Add Category" if lang == "English" else "➕ เพิ่มหมวดหมู่"):
                if new_cat and new_cat not in st.session_state.categories_list:
                    st.session_state.categories_list.append(new_cat)
                    st.success("Added category successfully.")
                    st.rerun()
                else:
                    st.warning("Category already exists or invalid.")

# เมนูที่ 4: รับสินค้า (Stock In)
elif selected_menu == t_ui["m4"]:
    st.title(f"{t_ui['m4']} - {selected_company}")
    if len(current_inv) == 0:
        st.warning("No items available." if lang == "English" else "ยังไม่มีรายการสินค้าในระบบ กรุณาเพิ่มรายการสินค้าก่อน")
    else:
        col_si1, col_si2, col_si3 = st.columns(3)
        with col_si1:
            si_date = st.date_input("Date" if lang == "English" else "วันที่รับสินค้า", value=datetime.today())
        with col_si2:
            existing_suppliers = current_inv["Supplier"].dropna().unique().tolist()
            si_supplier = st.selectbox("Supplier", existing_suppliers if existing_suppliers else ["CP Axtra (Makro)"])
        with col_si3:
            si_doc_no = st.text_input("Invoice No.")

        st.markdown("---")
        st.subheader("Stock In Cart" if lang == "English" else "เลือกและเพิ่มสินค้าเข้าตะกร้ารับเข้า")
        
        si_search_query = st.text_input("Search Product Code or Name" if lang == "English" else "🔍 พิมพ์รหัสสินค้า (Product Code) หรือ ชื่อสินค้า เพื่อดึงข้อมูลอัตโนมัติ", value="")
        
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
                    display_name_matched = translate_item_name(selected_item_name, lang)
                    st.success(f"Found [Code: {found_code}] -> **{display_name_matched}**")
                else:
                    st.error("Item not found.")
            else:
                st.info("Please type product code or name.")

            col_sq1, col_sq2, col_sq3 = st.columns(3)
            with col_sq1:
                si_qty = st.number_input("Quantity", min_value=0.1, value=1.0)
            with col_sq2:
                unit_idx = st.session_state.units_list.index(default_unit) if default_unit in st.session_state.units_list else 0
                si_unit = st.selectbox("Unit", st.session_state.units_list, index=unit_idx)
            with col_sq3:
                si_price = st.number_input("Price", min_value=0.0, value=default_price)

            add_to_si_cart = st.form_submit_button("Add to Stock In Cart" if lang == "English" else "➕ เพิ่มรายการนี้เข้าตะกร้ารับสินค้า")
            if add_to_si_cart:
                if selected_item_name:
                    st.session_state["temp_stock_in_cart"].append({
                        "Item Name": selected_item_name,
                        "Quantity": si_qty,
                        "Unit": si_unit,
                        "Price": si_price,
                        "Total": si_qty * si_price
                    })
                    st.success("Added!")
                    st.rerun()
                else:
                    st.error("Invalid item.")

        if len(st.session_state["temp_stock_in_cart"]) > 0:
            st.markdown("#### Cart")
            cart_df = pd.DataFrame(st.session_state["temp_stock_in_cart"])
            if lang == "English":
                cart_df["Item Name"] = cart_df["Item Name"].apply(lambda x: translate_item_name(x, lang))
            st.dataframe(cart_df, use_container_width=True)
            
            total_si_amount = cart_df["Total"].sum()
            st.markdown(f"### Total: **{total_si_amount:,.2f} THB**")

            col_sb1, col_sb2 = st.columns(2)
            with col_sb1:
                if st.button("Clear Cart"):
                    st.session_state["temp_stock_in_cart"] = []
                    st.rerun()
            with col_sb2:
                if st.button("Confirm Stock In"):
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
                            "Type": "Stock In",
                            "Item Name": i_name,
                            "Quantity": i_qty,
                            "Unit": i_unit,
                            "Note": f"Invoice: {si_doc_no} / Supplier: {si_supplier}"
                        }])
                        st.session_state["transaction_history"] = pd.concat([st.session_state["transaction_history"], new_trans], ignore_index=True)

                    st.session_state["temp_stock_in_cart"] = []
                    st.success("Stock updated successfully!")
                    st.rerun()

# เมนูที่ 5: เบิกสินค้า (Stock Out)
elif selected_menu == t_ui["m5"]:
    st.title(f"{t_ui['m5']} - {selected_company}")
    if len(current_inv) == 0:
        st.warning("No items available.")
    else:
        # แปลชื่อสินค้าในตัวเลือก Dropdown เบิกออกตามภาษา
        item_options = current_inv["Item Name"].tolist()
        display_item_options = [translate_item_name(x, lang) for x in item_options]

        with st.form("stock_out_form"):
            so_date = st.date_input("Date", value=datetime.today())
            selected_display_item = st.selectbox("Select Item", display_item_options)
            
            # แปลงกลับเป็นชื่อจริงในระบบเพื่อค้นหาข้อมูล
            so_item = item_options[display_item_options.index(selected_display_item)]
            
            default_unit = "หน่วย"
            current_bal = 0.0
            matched_item = current_inv[current_inv["Item Name"] == so_item]
            if not matched_item.empty:
                default_unit = str(matched_item.iloc[0]["Unit"])
                current_bal = float(matched_item.iloc[0]["Stock Balance"])

            st.info(f"Current Stock: **{current_bal} {default_unit}**")

            so_qty = st.number_input("Quantity", min_value=0.1, value=1.0)
            so_unit = st.selectbox("Unit", st.session_state.units_list, index=st.session_state.units_list.index(default_unit) if default_unit in st.session_state.units_list else 0)
            so_note = st.text_input("Note / Department")

            submit_so = st.form_submit_button("Confirm Stock Out")
            if submit_so:
                if so_qty > current_bal:
                    st.error("Insufficient stock!")
                else:
                    inv = st.session_state["company_inventories"][selected_company]
                    idx = inv.index[inv["Item Name"] == so_item][0]
                    inv.loc[idx, "Stock Balance"] -= so_qty
                    
                    new_trans = pd.DataFrame([{
                        "Date": str(so_date),
                        "Branch": selected_company,
                        "Type": "Stock Out",
                        "Item Name": so_item,
                        "Quantity": so_qty,
                        "Unit": so_unit,
                        "Note": so_note
                    }])
                    st.session_state["transaction_history"] = pd.concat([st.session_state["transaction_history"], new_trans], ignore_index=True)
                    st.success("Stock out successful!")
                    st.rerun()

# เมนูที่ 6: ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)
elif selected_menu == t_ui["m6"]:
    st.title(f"{t_ui['m6']} - {selected_company}")
    pr_tab1, pr_tab2 = st.tabs(["📄 1. PR", "📦 2. PO"])

    with pr_tab1:
        st.subheader("Create PR")
        if "temp_pr_cart" not in st.session_state:
            st.session_state["temp_pr_cart"] = []
        st.info("PR system active.")

    with pr_tab2:
        st.subheader("Purchase Orders (PO)")
        st.info("PO system active.")

# เมนูที่ 7: ประวัติการทำรายการ
elif selected_menu == t_ui["m7"]:
    st.title(f"{t_ui['m7']} - {selected_company}")
    if len(st.session_state["transaction_history"]) > 0:
        hist_df = st.session_state["transaction_history"].copy()
        if lang == "English":
            hist_df["Item Name"] = hist_df["Item Name"].apply(lambda x: translate_item_name(x, lang))
        st.dataframe(hist_df, use_container_width=True)
    else:
        st.info("No transaction history.")

# เมนูที่ 8: รายการสรุปสต็อก & นับสต็อก
elif selected_menu == t_ui["m8"]:
    st.title(f"{t_ui['m8']} - {selected_company}")
    if len(display_inv) > 0:
        st.dataframe(display_inv, use_container_width=True)
    else:
        st.info("No stock data.")

# เมนูที่ 9: ตั้งค่าข้อมูลบริษัทและแอดมิน
elif selected_menu == t_ui["m9"]:
    st.title(f"{t_ui['m9']} - {selected_company}")
    st.info("Settings panel.")
