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
    st.session_state.units_list = [
        "Bag",
        "Bottle",
        "Box",
        "Can",
        "Case",
        "Cup",
        "Gallon",
        "Gram",
        "Jar",
        "Kg.",
        "Litre",
        "Pack",
        "Pcs."
    ]

if "categories_list" not in st.session_state:
    st.session_state.categories_list = [
        "ไวน์",
        "น้ำผลไม้/ผลไม้สด-เครื่องดื่ม",
        "เนื้อวัว",
        "อาหารทะเล",
        "ผักและผลไม้-อาหาร",
        "เนย/ชีส/ซาลามิ/แฮม",
        "เนื้อสัตว์/เครื่องปรุง/วัตถุดิบอื่นๆ",
        "เนื้อแกะ",
        "แซลมอนรมควัน",
        "เบียร์กระป๋อง/เบียร์สด/น้ำอัดลม",
        "เมล็ดกาแฟ",
        "ขนมปัง/เบเกอรี่/ของหวาน/ไอศกรีม"
    ]

if "companies_list" not in st.session_state:
    st.session_state.companies_list = [
        "Daddy Deli",
        "Daddy Deli Beach House",
        "Daddy Deli Pattaya Group",
        "Harvest Cafe",
        "Taboo By Daddy Deli",
        "Harvest Bakery And Restaurant"
    ]

if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "owner_master": {
            "name": "คุณเจ้าของ (Owner)", 
            "phone": "081-111-1111",
            "email": "owner@daddydeli.com",
            "role": "Owner", 
            "branches": st.session_state.companies_list  
        },
        "manager_general": {
            "name": "ผู้จัดการทั่วไป (Manager)", 
            "phone": "082-222-2222",
            "email": "manager@daddydeli.com",
            "role": "Manager", 
            "branches": st.session_state.companies_list  
        },
        "admin_daddy_deli": {
            "name": "แอดมิน (เฉพาะ Daddy Deli)", 
            "phone": "083-333-3333",
            "email": "admin1@daddydeli.com",
            "role": "Admin", 
            "branches": ["Daddy Deli"]  
        }
    }

if "company_details" not in st.session_state:
    st.session_state["company_details"] = {
        "Daddy Deli": {
            "shop_name": "Daddy Deli Hua Hin",
            "name": "บริษัท เดอะ เล็ค ล็อดจ์ กรุ๊ป จำกัด ( สำนักงานใหญ่ )",
            "address": "No.17 Moo.7 Hin Lek Fai Subdistrict, Hua Hin District, Prachuap Khiri Khan Province 77110",
            "tax_id": "0775565003672",
            "admin_contact": "คุณแอดมิน (083-333-3333)",
            "role_permission": "Admin (เฉพาะสาขา)",
            "contact": "0775565003672"
        },
        "Daddy Deli Beach House": {
            "shop_name": "Daddy Deli Beach House",
            "name": "บริษัท แดดดี้ส์ เดลี่ บีชเฮ้าส์ จำกัด ( สำนักงานใหญ่ )",
            "address": "No.19 Soi Moo Ban Khaotao, Nong Kae, Hua Hin, Prachuap Khiri Khan Province 77110",
            "tax_id": "0775569000872",
            "admin_contact": "-",
            "role_permission": "Manager",
            "contact": "0775569000872"
        },
        "Daddy Deli Pattaya Group": {
            "shop_name": "Daddy Deli Pattaya",
            "name": "บริษัท แดดดี้ส์ เดลี่ พัทยา กรุ๊ป จำกัด ( สำนักงานใหญ่ )",
            "address": "No.391/116 Moo 10, Nong Prue Subdistrict, Bang Lamung District, Chonburi Province 20150",
            "tax_id": "0205569016935",
            "admin_contact": "-",
            "role_permission": "Manager",
            "contact": "0205569016935"
        },
        "Harvest Cafe": {
            "shop_name": "Harvest Cafe",
            "name": "บริษัท เดอะ เล็ค ล็อดจ์ กรุ๊ป จำกัด ( สาขา 0001 )",
            "address": "779 Village No.7 Hin Lek Fai Subdistrict, Hua Hin District, Prachuap Khiri Khan Province 77110",
            "tax_id": "0775565003672",
            "admin_contact": "-",
            "role_permission": "Manager",
            "contact": "0775565003672"
        },
        "Taboo By Daddy Deli": {
            "shop_name": "Taboo",
            "name": "บริษัท เดอะ เล็ค ล็อดจ์ กรุ๊ป จำกัด ( สาขา 0002 )",
            "address": "No.10/238 Soi Moo Ban Samor Phrong, Hua Hin District, Prachuap Khiri Khan Province 77110",
            "tax_id": "0775565003672",
            "admin_contact": "-",
            "role_permission": "Manager",
            "contact": "0775565003672"
        },
        "Harvest Bakery And Restaurant": {
            "shop_name": "Harvest Bakery",
            "name": "บริษัท ฮาร์เวสต์ เบเกอรี่ แอนด์ เรสเตอรองต์ จำกัด ( สำนักงานใหญ่ )",
            "address": "779 Village No.7 Hin Lek Fai Subdistrict, Hua Hin District, Prachuap Khiri Khan Province 77110",
            "tax_id": "0775569002727",
            "admin_contact": "-",
            "role_permission": "Manager",
            "contact": "0775569002727"
        }
    }

if "company_logos" not in st.session_state:
    st.session_state["company_logos"] = {}

if "company_inventories" not in st.session_state:
    initial_demo_df = pd.DataFrame([
        {
            "Product Code": "1950",
            "Item Name": "นมจืด 2 ลิตร",
            "Category": "น้ำผลไม้/ผลไม้สด-เครื่องดื่ม",
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
        if comp == "Daddy Deli":
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
# 2. DICTIONARY TRANSLATIONS & MAPPINGS
# ----------------------------------------------------
item_translations = {
    "นมจืด 2 ลิตร": "Fresh Milk 2 Liters"
}

category_translations = {
    "ไวน์": "Wine",
    "น้ำผลไม้/ผลไม้สด-เครื่องดื่ม": "Juice/Fresh Fruit-Beverage",
    "เนื้อวัว": "Beef",
    "อาหารทะเล": "Seafood",
    "ผักและผลไม้-อาหาร": "Vegetables & Fruits-Food",
    "เนย/ชีส/ซาลามิ/แฮม": "Butter/Cheese/Salami/Ham",
    "เนื้อสัตว์/เครื่องปรุง/วัตถุดิบอื่นๆ": "Meat/Condiments/Other Ingredients",
    "เนื้อแกะ": "Lamb",
    "แซลมอนรมควัน": "Smoked Salmon",
    "เบียร์กระป๋อง/เบียร์สด/น้ำอัดลม": "Canned Beer/Draft Beer/Soft Drinks",
    "เมล็ดกาแฟ": "Coffee Beans",
    "ขนมปัง/เบเกอรี่/ของหวาน/ไอศกรีม": "Bread/Bakery/Dessert/Ice Cream"
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
        "m9": "⚙️ ตั้งค่าข้อมูลบริษัทและแอดมิน"
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
        "m9": "⚙️ Settings"
    }
}

# ----------------------------------------------------
# 3. SIDEBAR CONFIGURATION & ROLE-BASED ACCESS CONTROL
# ----------------------------------------------------
st.sidebar.markdown("### 🌐 ภาษา / Language")
lang = st.sidebar.selectbox("Language", ["ไทย (Thai)", "English"], label_visibility="collapsed")
t_ui = texts[lang]

st.sidebar.markdown(f"### {t_ui['user_title']}")
current_user_key = st.sidebar.selectbox("User", list(st.session_state.users_db.keys()), label_visibility="collapsed")
current_user_data = st.session_state.users_db[current_user_key]

user_role = current_user_data["role"]
allowed_branches = current_user_data["branches"]

st.sidebar.markdown(f"### {t_ui['company_title']}")
selected_company = st.sidebar.selectbox("Company", allowed_branches, label_visibility="collapsed")

curr_comp_details = st.session_state["company_details"].get(selected_company, {})
comp_display_name = curr_comp_details.get('shop_name', selected_company)

st.sidebar.markdown(f"**{comp_display_name}**")
st.sidebar.caption(f"Address: {curr_comp_details.get('address', '-')}\n\nTax ID: {curr_comp_details.get('tax_id', '-')}")
st.sidebar.info(f"**{current_user_data['name']}**\n\nRole: **{user_role}**\n\nAccess Branches: {', '.join(allowed_branches)}")

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

display_inv = current_inv.copy()
if len(display_inv) > 0 and lang == "English":
    display_inv["Item Name"] = display_inv["Item Name"].apply(lambda x: translate_item_name(x, lang))
    display_inv["Category"] = display_inv["Category"].apply(lambda x: translate_category(x, lang))

# ----------------------------------------------------
# 5. ROUTING LOGIC
# ----------------------------------------------------

if selected_menu == t_ui["m1"]:
    st.title(f"{t_ui['m1']} - {comp_display_name}")
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

elif selected_menu == t_ui["m2"]:
    st.title(f"{t_ui['m2']} - {comp_display_name}")
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

elif selected_menu == t_ui["m3"]:
    st.title(f"{t_ui['m3']} - {comp_display_name}")
    elif selected_menu == t_ui["m3"]:
    st.title(f"{t_ui['m3']} - {comp_display_name}")
    st.markdown("กรอกข้อมูลเพื่อเพิ่มรายการสินค้าใหม่เข้าสู่ระบบสต็อกของสาขานี้")

    with st.form("add_new_item_form"):
        new_code = st.text_input("รหัสสินค้า (Product Code)")
        new_name = st.text_input("ชื่อสินค้า (Item Name)")
        new_supplier = st.text_input("ชื่อร้านค้า / Supplier (เช่น Makro, Gourmet Market)")
        new_category = st.selectbox("หมวดหมู่สินค้า", st.session_state.categories_list)
        new_unit = st.selectbox("หน่วยนับ", st.session_state.units_list)
        new_conv = st.number_input("อัตราส่วนการแปลงหน่วย (Conversion Qty)", value=1.0, min_value=0.01)
        new_price = st.number_input("ราคาล่าสุด (Last Price)", value=0.0, min_value=0.0)
        new_vat = st.selectbox("ประเภท Vat", VAT_TYPES_LIST)
        new_initial_stock = st.number_input("จำนวนสต็อกเริ่มต้น (Initial Stock Balance)", value=0.0, min_value=0.0)

        submitted_new_item = st.form_submit_button("💾 บันทึกเพิ่มสินค้าใหม่")
        if submitted_new_item:
            if not new_name.strip():
                st.error("⚠️ กรุณากรอกชื่อสินค้า")
            else:
                new_row = pd.DataFrame([{
                    "Product Code": new_code,
                    "Item Name": new_name,
                    "Category": new_category,
                    "Unit": new_unit,
                    "Conversion Qty": new_conv,
                    "Stock Balance": new_initial_stock,
                    "Last Price": new_price,
                    "Supplier": new_supplier,
                    "Vat Type": new_vat
                }])
                st.session_state["company_inventories"][selected_company] = pd.concat(
                    [st.session_state["company_inventories"][selected_company], new_row], 
                    ignore_index=True
                )
                st.success(f"✨ เพิ่มสินค้า '{new_name}' สำเร็จเรียบร้อยแล้ว!")
                st.rerun()

elif selected_menu == t_ui["m4"]:
    st.title(f"{t_ui['m4']} - {comp_display_name}")

elif selected_menu == t_ui["m5"]:
    st.title(f"{t_ui['m5']} - {comp_display_name}")

elif selected_menu == t_ui["m6"]:
    st.title(f"{t_ui['m6']} - {comp_display_name}")

elif selected_menu == t_ui["m7"]:
    st.title(f"{t_ui['m7']} - {comp_display_name}")

elif selected_menu == t_ui["m8"]:
    st.title(f"{t_ui['m8']} - {comp_display_name}")

elif selected_menu == t_ui["m9"]:
    st.title(f"{t_ui['m9']} - {comp_display_name}")
    
    tab_comp, tab_admin = st.tabs(["🏢 1. ตั้งค่าข้อมูลบริษัท/สาขา", "👤 2. เพิ่มแอดมิน/ผู้ดูแล"])

    with tab_comp:
        curr_details = st.session_state["company_details"].get(selected_company, {
            "shop_name": selected_company, "name": "", "address": "", "tax_id": "", "admin_contact": "", "role_permission": ""
        })
        existing_logo = st.session_state["company_logos"].get(selected_company)
        if existing_logo is not None:
            st.image(existing_logo, width=150, caption="โลโก้ปัจจุบันของบริษัท/สาขา")
        
        with st.form("company_info_form_ordered"):
            # 1. ชื่อร้าน
            c_shop_name = st.text_input("1. ชื่อร้าน", value=curr_details.get("shop_name", selected_company))
            # 2. ชื่อบริษัท/สาขา
            c_name = st.text_input("2. ชื่อบริษัท/สาขา", value=curr_details.get("name", ""))
            # 3. ที่อยู่
            c_address = st.text_area("3. ที่อยู่", value=curr_details.get("address", ""))
            # 4. เลขที่ผู้เสียภาษี
            c_tax = st.text_input("4. เลขที่ผู้เสียภาษี", value=curr_details.get("tax_id", ""))
            # 5. ข้อมูลแอดมิน/ผู้ดูแล
            c_admin_contact = st.text_input("5. ข้อมูลแอดมิน/ผู้ดูแล", value=curr_details.get("admin_contact", ""))
            # 6. กำหนดสิทธิ
            c_role_permission = st.selectbox("6. กำหนดสิทธิ", ["เจ้าของ = ดูข้อมูลได้ทุกบริษัท/สาขา", "Manager = ดูข้อมูลได้ทุกบริษัท/สาขา", "Admin = ดูได้แค่บริษัท/สาขา ที่กำหนด"], index=0)
            # 7. โลโก้บริษัท/สาขา
            uploaded_logo = st.file_uploader("7. โลโก้บริษัท/สาขา", type=["png", "jpg", "jpeg"], key="logo_settings_page_v2")

            if st.form_submit_button("💾 บันทึกข้อมูลบริษัท/สาขา"):
                st.session_state["company_details"][selected_company] = {
                    "shop_name": c_shop_name,
                    "name": c_name,
                    "address": c_address,
                    "tax_id": c_tax,
                    "admin_contact": c_admin_contact,
                    "role_permission": c_role_permission,
                    "contact": c_tax
                }
                if uploaded_logo is not None:
                    st.session_state["company_logos"][selected_company] = uploaded_logo
                st.success("บันทึกข้อมูลบริษัท/สาขาเรียบร้อยแล้ว!")
                st.rerun()

    with tab_admin:
        st.subheader("เพิ่มแอดมิน/ผู้ดูแลระบบใหม่")
        with st.form("add_admin_form"):
            # 1. ชื่อแอดมิน/ผู้ดูแล
            new_admin_name = st.text_input("1. ชื่อแอดมิน/ผู้ดูแล")
            # 2. เบอร์โทร
            new_admin_phone = st.text_input("2. เบอร์โทร")
            # 3. อีเมลล์
            new_admin_email = st.text_input("3. อีเมลล์")
            # 4. สิทธิในการดูแล
            new_admin_role = st.selectbox(
                "4. สิทธิในการดูแล",
                [
                    "เจ้าของ = ดูข้อมูลได้ทุกบริษัท/สาขา",
                    "Manager = ดูข้อมูลได้ทุกบริษัท/สาขา",
                    "Admin = ดูได้แค่บริษัท/สาขา ที่กำหนด"
                ]
            )
            # 5. บริษัท/สาขา ที่ดูแล
            new_admin_branch = st.selectbox(
                "5. บริษัท/สาขา ที่ดูแล",
                st.session_state.companies_list
            )

            submit_admin = st.form_submit_button("💾 บันทึกผู้ดูแลระบบใหม่")
            if submit_admin:
                if not new_admin_name.strip() or not new_admin_email.strip():
                    st.error("⚠️ กรุณากรอกชื่อและอีเมลล์ให้ครบถ้วน")
                else:
                    if "เจ้าของ" in new_admin_role:
                        role_key = "Owner"
                        assigned_branches = st.session_state.companies_list
                    elif "Manager" in new_admin_role:
                        role_key = "Manager"
                        assigned_branches = st.session_state.companies_list
                    else:
                        role_key = "Admin"
                        assigned_branches = [new_admin_branch]

                    user_key_id = f"user_{len(st.session_state.users_db) + 1}"
                    st.session_state.users_db[user_key_id] = {
                        "name": new_admin_name,
                        "phone": new_admin_phone,
                        "email": new_admin_email,
                        "role": role_key,
                        "branches": assigned_branches
                    }
                    st.success(f"✨ เพิ่มแอดมิน '{new_admin_name}' เรียบร้อยแล้ว!")
                    st.rerun()
