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
# 1. INITIALIZE SESSION STATES (อัปเดตหมวดหมู่และหน่วยนับใหม่)
# ----------------------------------------------------
st.session_state.units_list = [
    "Bag", "Bottle", "Box", "Can", "Case", "Cup", 
    "Gallon", "Gram", "Jar", "Kg.", "Litre", "Pack", "Pcs."
]

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
   
    # --- ส่วนค้นหาข้อมูลสินค้า (วางแทนที่โค้ดค้นหาอันเดิมด้านบนสุดของหน้า m2) ---
    st.markdown("### 🔍 ค้นหาข้อมูลสินค้า")

    # สร้างตัวเลือก Dropdown สำหรับ Supplier
    sup_search_options = ["ทั้งหมด"] + [s["name"] for s in st.session_state.get("suppliers_list", [])]
    if len(sup_search_options) == 1:
        sup_search_options = ["ทั้งหมด", "Makro", "Gourmet Market"]

    # สร้างตัวเลือก Dropdown สำหรับหมวดหมู่
    cat_search_options = ["ทั้งหมด"] + list(st.session_state.get("categories_list", []))

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        # เปลี่ยนเป็น Dropdown ค้นหาตามชื่อร้านค้า
        search_supplier = st.selectbox("ค้นหาตามชื่อร้านค้า (Supplier)", sup_search_options)
    with col_s2:
        search_code = st.text_input("ค้นหารหัสสินค้า (Product Code)")
    with col_s3:
        # เปลี่ยนเป็น Dropdown ค้นหาตามหมวดหมู่
        search_category = st.selectbox("ค้นหาตามหมวดหมู่ (Category)", cat_search_options)
    
        filtered_df = display_inv.copy()
        if search_supplier and search_supplier != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df["Supplier"].astype(str).str.contains(search_supplier, case=False, na=False)]
        if search_code:
            filtered_df = filtered_df[filtered_df["Product Code"].astype(str).str.contains(search_code, case=False, na=False)]
        if search_category not in ["All", "ทั้งหมด"]:
            filtered_df = filtered_df[filtered_df["Category"] == search_category]
# --- ส่วนแสดงรายการสินค้าทั้งหมดและการจัดการ ---
    st.markdown("---")
    st.markdown("### 📋 รายการสินค้าทั้งหมดในระบบของสาขานี้ & จัดการ")
    
    current_inv = st.session_state["company_inventories"].get(selected_company, pd.DataFrame())
    if current_inv.empty:
        st.info("ยังไม่มีรายการสินค้าในระบบ")
    else:
        for i, row in current_inv.iterrows():
            # 1. จัดเรียงลำดับใหม่เป็น: ร้าน, รหัส, ชื่อสินค้า, หมวดหมู่, คงเหลือ
            display_text = (
                f"🏪 **ร้าน:** {row.get('Supplier', '-')} | "
                f"📌 **รหัส:** {row.get('Product Code', '-')} | "
                f"📦 **ชื่อสินค้า:** **{row.get('Item Name', '-')}** | "
                f"🏷️ **หมวดหมู่:** {row.get('Category', '-')} | "
                f"🔢 **คงเหลือ:** {row.get('Stock Balance', 0)} {row.get('Unit', '')} | "
                f"💰 **ราคา:** {row.get('Last Price', 0):,.2f} ฿"
            )
            
            cols_item = st.columns([4, 1])
            cols_item[0].write(display_text)
            
            action_item = cols_item[1].selectbox("จัดการ", ["เลือก", "แก้ไข", "ลบ"], key=f"action_item_{i}", label_visibility="collapsed")
            
            if action_item == "ลบ":
                st.session_state["company_inventories"][selected_company] = current_inv.drop(i).reset_index(drop=True)
                st.success("🗑️ ลบรายการสินค้าเรียบร้อยแล้ว")
                st.rerun()
            elif action_item == "แก้ไข":
                st.session_state[f"edit_mode_item_{i}"] = True

            # 2. ฟอร์มแก้ไขแบบเต็มหน้าจอ (แสดงเมื่อกดแก้ไข)
            if st.session_state.get(f"edit_mode_item_{i}", False):
                st.markdown(f"---")
                with st.container():
                    st.warning(f"✏️ กำลังแก้ไขสินค้า: {row.get('Item Name', '')}")
                    with st.form(f"form_edit_item_{i}"):
                        ed_code = st.text_input("รหัสสินค้า (Product Code)", value=str(row.get('Product Code', '')))
                        ed_name = st.text_input("ชื่อสินค้า (Item Name)", value=str(row.get('Item Name', '')))
                        
                        # ดึงรายชื่อ Supplier และ Category ที่มีมาให้เลือก
                        sup_list = [s.get('name', '') for s in st.session_state.get('suppliers_list', [])]
                        if not sup_list: sup_list = [str(row.get('Supplier', ''))]
                        current_sup = str(row.get('Supplier', ''))
                        sup_idx = sup_list.index(current_sup) if current_sup in sup_list else 0
                        ed_supplier = st.selectbox("ชื่อร้านค้า (Supplier)", sup_list, index=sup_idx)
                        
                        cat_list = st.session_state.get('categories_list', ['ทั่วไป'])
                        current_cat = str(row.get('Category', 'ทั่วไป'))
                        cat_idx = cat_list.index(current_cat) if current_cat in cat_list else 0
                        ed_category = st.selectbox("หมวดหมู่สินค้า", cat_list, index=cat_idx)
                        
                        ed_price = st.number_input("ราคารวม Vat", value=float(row.get('Last Price', 0.0)), format="%.2f")
                        ed_vat = st.selectbox("Vat Type", ["Vat 7%", "Non Vat"], index=0 if row.get('Vat Type', '') == "Vat 7%" else 1)
                        
                        c_i1, c_i2 = st.columns(2)
                        with c_i1:
                            sub_edit_item = st.form_submit_button("💾 บันทึกการแก้ไข")
                        with c_i2:
                            sub_cancel_item = st.form_submit_button("❌ ยกเลิก")

                        if sub_edit_item:
                            # บันทึกข้อมูลลง DataFrame
                            st.session_state["company_inventories"][selected_company].loc[i, 'Product Code'] = ed_code
                            st.session_state["company_inventories"][selected_company].loc[i, 'Item Name'] = ed_name
                            st.session_state["company_inventories"][selected_company].loc[i, 'Supplier'] = ed_supplier
                            st.session_state["company_inventories"][selected_company].loc[i, 'Category'] = ed_category
                            st.session_state["company_inventories"][selected_company].loc[i, 'Last Price'] = ed_price
                            st.session_state["company_inventories"][selected_company].loc[i, 'Vat Type'] = ed_vat
                            
                            # ปิดโหมดแก้ไข (ให้ฟอร์มพับเก็บกลับไป)
                            st.session_state[f"edit_mode_item_{i}"] = False
                            st.success(f"✅ บันทึกการแก้ไขสินค้า '{ed_name}' เรียบร้อยแล้ว!")
                            st.rerun()
                            
                        if sub_cancel_item:
                            st.session_state[f"edit_mode_item_{i}"] = False
                            st.rerun()
                st.markdown(f"---")
  
elif selected_menu == t_ui["m3"]:
    st.title(f"{t_ui['m3']} - {comp_display_name}")
    st.markdown("กรอกข้อมูลเพื่อเพิ่มรายการสินค้าใหม่เข้าสู่ระบบของสาขานี้ หรือจัดการข้อมูลพื้นฐาน")

    tab_add_item, tab_manage_unit, tab_manage_cat, tab_manage_supplier = st.tabs([
        "➕ เพิ่มสินค้าใหม่",
        "📏 จัดการหน่วยนับ",
        "🏷️ จัดการหมวดหมู่สินค้า",
        "🏢 จัดการ/เพิ่มบริษัทจัดซื้อสินค้า"
    ])
# --- Tab 1: เพิ่มสินค้าใหม่ ---
    with tab_add_item:
        st.markdown("### ✍️ เพิ่มรายการสินค้าใหม่ด้วยตนเอง")
        
        with st.form("manual_add_item_form"):
            # ดึงรายชื่อ Supplier จากที่มีอยู่ในระบบมาทำดรอปดาวน์ (ถ้ามี)
            existing_sup_names = [s.get('name', '') for s in st.session_state.get('suppliers_list', [])]
            if not existing_sup_names:
                existing_sup_names = ["CP Axtra (Makro)"]
                
            manual_supplier = st.selectbox("1. ชื่อร้านค้า (Supplier)", existing_sup_names)
            manual_code = st.text_input("2. รหัสสินค้า (Product Code)")
            manual_name = st.text_input("3. ชื่อสินค้า (Item Name)")
            manual_price = st.number_input("4. ราคาสินค้า (รวม Vat)", min_value=0.0, format="%.2f")
            manual_vat_type = st.selectbox("5. Vat / Non Vat", ["Vat 7%", "Non Vat"])
            
            submitted_manual_item = st.form_submit_button("💾 บันทึกสินค้าใหม่เข้าสู่ระบบ")

        if submitted_manual_item:
            if not manual_name.strip():
                st.error("⚠️ กรุณากรอกชื่อสินค้า")
            else:
                # สร้าง DataFrame สำหรับสินค้าใหม่ที่กรอกเข้ามา
                new_manual_row = pd.DataFrame([{
                    "Product Code": str(manual_code).strip(),
                    "Item Name": str(manual_name).strip(),
                    "Category": "ทั่วไป",
                    "Unit": "หน่วย",
                    "Conversion Qty": 1.0,
                    "Stock Balance": 0.0,
                    "Last Price": float(manual_price),
                    "Supplier": str(manual_supplier),
                    "Vat Type": str(manual_vat_type)
                }])
                
                # บันทึกลงใน session state ของสาขานั้นๆ
                st.session_state["company_inventories"][selected_company] = pd.concat(
                    [st.session_state["company_inventories"][selected_company], new_manual_row],
                    ignore_index=True
                )
                st.success(f"✨ บันทึกสินค้า '{manual_name}' เรียบร้อยแล้ว!")
                st.rerun()

        st.markdown("---")
        st.markdown("### 📊 หรือนำเข้าสินค้าผ่านไฟล์ Excel")
        uploaded_excel = st.file_uploader("เลือกไฟล์ Excel (รองรับ .xlsx, .xls)", type=["xlsx", "xls"], key="upload_excel_m3")

        if uploaded_excel is not None:
            try:
                df_excel = pd.read_excel(uploaded_excel)
                st.write("ตัวอย่างข้อมูลจากไฟล์ Excel:")
                st.dataframe(df_excel.head())

                if st.button("🚀 บันทึกข้อมูลจาก Excel เข้าสู่ระบบ"):
                    for idx_ex, row_ex in df_excel.iterrows():
                        new_excel_row = pd.DataFrame([{
                            "Product Code": str(row_ex.get("Product Code", "")),
                            "Item Name": str(row_ex.get("Item Name", "")),
                            "Category": str(row_ex.get("Category", "")),
                            "Unit": str(row_ex.get("Unit", "")),
                            "Conversion Qty": float(row_ex.get("Conversion Qty", 1.0)),
                            "Stock Balance": float(row_ex.get("Stock Balance", 0.0)),
                            "Last Price": float(row_ex.get("Last Price", 0.0)),
                            "Supplier": str(row_ex.get("Supplier", "")),
                        }])
                        st.session_state["company_inventories"][selected_company] = pd.concat(
                            [st.session_state["company_inventories"][selected_company], new_excel_row],
                            ignore_index=True
                        )
                    st.success("✅ นำเข้าข้อมูลสินค้าจาก Excel สำเร็จเรียบร้อยแล้ว!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์ Excel: {e}")

        # --- ส่วนแสดงรายการสินค้าทั้งหมดด้านล่างสุด พร้อมปุ่มจัดการ (แก้ไข/ลบ) ---
        st.markdown("---")
        st.markdown("### 📋 รายการสินค้าทั้งหมดในระบบของสาขานี้ & จัดการ")
        
        current_inv = st.session_state["company_inventories"].get(selected_company, pd.DataFrame())
        if current_inv.empty:
            st.info("ยังไม่มีรายการสินค้าในระบบ")
        else:
            for i, row in current_inv.iterrows():
                cols_item = st.columns([3, 1.5])
                cols_item[0].write(f"**[{row.get('Product Code', '-')}] {row.get('Item Name', '-')}**\n- ร้านค้า: {row.get('Supplier', '-')} | ราคา: {row.get('Last Price', 0):,.2f} บาท ({row.get('Vat Type', 'Vat 7%')})")
                
                action_item = cols_item[1].selectbox("จัดการ", ["เลือก", "แก้ไข", "ลบ"], key=f"action_item_{i}", label_visibility="collapsed")
                
                if action_item == "ลบ":
                    st.session_state["company_inventories"][selected_company] = current_inv.drop(i).reset_index(drop=True)
                    st.success("🗑️ ลบรายการสินค้าเรียบร้อยแล้ว")
                    st.rerun()
                elif action_item == "แก้ไข":
                    st.session_state[f"edit_mode_item_{i}"] = True

                if st.session_state.get(f"edit_mode_item_{i}", False):
                    with st.form(f"form_edit_item_{i}"):
                        st.markdown(f"##### แก้ไขสินค้า: {row.get('Item Name', '')}")
                        ed_code = st.text_input("รหัสสินค้า", value=str(row.get('Product Code', '')))
                        ed_name = st.text_input("ชื่อสินค้า", value=str(row.get('Item Name', '')))
                        ed_price = st.number_input("ราคารวม Vat", value=float(row.get('Last Price', 0.0)), format="%.2f")
                        ed_vat = st.selectbox("Vat Type", ["Vat 7%", "Non Vat"], index=0 if row.get('Vat Type', '') == "Vat 7%" else 1)
                        
                        c_i1, c_i2 = st.columns(2)
                        with c_i1:
                            sub_edit_item = st.form_submit_button("💾 บันทึกการแก้ไข")
                        with c_i2:
                            sub_cancel_item = st.form_submit_button("❌ ยกเลิก")

                        if sub_edit_item:
                            st.session_state["company_inventories"][selected_company].loc[i, 'Product Code'] = ed_code
                            st.session_state["company_inventories"][selected_company].loc[i, 'Item Name'] = ed_name
                            st.session_state["company_inventories"][selected_company].loc[i, 'Last Price'] = ed_price
                            st.session_state["company_inventories"][selected_company].loc[i, 'Vat Type'] = ed_vat
                            st.session_state[f"edit_mode_item_{i}"] = False
                            st.success("✅ แก้ไขข้อมูลสินค้าสำเร็จ")
                            st.rerun()
                            
                        if sub_cancel_item:
                            st.session_state[f"edit_mode_item_{i}"] = False
                            st.rerun()
                            
                    st.markdown("---")
                
   # --- Tab 2: จัดการหน่วยนับ (Units) ---
    with tab_unit:  # แก้จาก tab_units เป็น tab_unit ตามตัวแปรหลัก
        st.markdown("### 📏 จัดการหน่วยนับ (Units)")
        
        # ตรวจสอบและสร้างตัวแปรเก็บรายการหน่วยนับใน session_state ถ้ายังไม่มี
        if "units_list" not in st.session_state:
            st.session_state["units_list"] = ["Bag", "Bottle", "Box", "Can", "Case", "Cup", "Gallon", "Gram", "Jar", "Kg.", "Litre", "Pack", "Pcs."]

        with st.form("form_add_unit"):
            new_unit_name = st.text_input("ชื่อหน่วยนับใหม่ (เช่น แพ็ค, กิโลกรัม)")
            submitted_unit = st.form_submit_button("💾 บันทึกหน่วยนับใหม่")

        if submitted_unit:
            if not new_unit_name.strip():
                st.error("⚠️ กรุณากรอกชื่อหน่วยนับ")
            else:
                # ตรวจสอบว่ามีหน่วยนับนี้อยู่แล้วหรือยัง (กันซ้ำ)
                if new_unit_name.strip() in st.session_state["units_list"]:
                    st.warning(f"⚠️ หน่วยนับ '{new_unit_name.strip()}' มีอยู่ในระบบอยู่แล้ว")
                else:
                    # เพิ่มหน่วยนับใหม่เข้าไปในรายการ
                    st.session_state["units_list"].append(new_unit_name.strip())
                    st.success(f"✨ บันทึกหน่วยนับ '{new_unit_name.strip()}' เรียบร้อยแล้ว!")
                    st.rerun()

        st.markdown("---")
        st.markdown("### 📋 รายชื่อหน่วยนับที่มีอยู่ & จัดการ/ลบ")

        if not st.session_state["units_list"]:
            st.info("ยังไม่มีรายการหน่วยนับในระบบ")
        else:
            for idx, u_item in enumerate(st.session_state["units_list"]):
                cols_u = st.columns([4, 1, 1])
                cols_u[0].write(f"• {u_item}")
                
                btn_edit_u = cols_u[1].button("✏️ แก้ไข", key=f"btn_edit_u_{idx}")
                btn_del_u = cols_u[2].button("🗑️ ลบ", key=f"btn_del_u_{idx}")

                if btn_del_u:
                    st.session_state["units_list"].pop(idx)
                    st.success(f"🗑️ ลบหน่วยนับ '{u_item}' เรียบร้อยแล้ว")
                    st.rerun()

                if btn_edit_u:
                    st.session_state[f"edit_mode_unit_{idx}"] = True

                if st.session_state.get(f"edit_mode_unit_{idx}", False):
                    with st.form(f"form_edit_unit_{idx}"):
                        edited_u_name = st.text_input("แก้ไขชื่อหน่วยนับ", value=u_item, key=f"input_edit_u_{idx}")
                        c_ue1, c_ue2 = st.columns(2)
                        sub_edit_u = c_ue1.form_submit_button("💾 บันทึก")
                        sub_cancel_u = c_ue2.form_submit_button("❌ ยกเลิก")

                        if sub_edit_u:
                            if edited_u_name.strip():
                                st.session_state["units_list"][idx] = edited_u_name.strip()
                                st.session_state[f"edit_mode_unit_{idx}"] = False
                                st.success("✅ แก้ไขหน่วยนับสำเร็จ")
                                st.rerun()
                            else:
                                st.error("⚠️ กรุณากรอกชื่อหน่วยนับ")
                        if sub_cancel_u:
                            st.session_state[f"edit_mode_unit_{idx}"] = False
                            st.rerun()

    # --- Tab 3: จัดการหมวดหมู่สินค้า ---
    with tab_manage_cat:
        st.subheader("จัดการหมวดหมู่สินค้า (Categories)")
        
        with st.form("add_cat_form"):
            new_cat_input = st.text_input("ชื่อหมวดหมู่สินค้าใหม่ (เช่น เครื่องดื่ม, ของสด)")
            submitted_cat = st.form_submit_button("💾 บันทึกหมวดหมู่ใหม่")

        if submitted_cat:
            if new_cat_input.strip():
                if new_cat_input not in st.session_state.categories_list:
                    st.session_state.categories_list.append(new_cat_input)
                    st.success(f"✅ บันทึกหมวดหมู่ '{new_cat_input}' เรียบร้อยแล้ว!")
                    st.rerun()
                else:
                    st.warning(f"⚠️ หมวดหมู่นี้มีอยู่แล้วในระบบ")
            else:
                st.warning("⚠️ กรุณากรอกชื่อหมวดหมู่")

        st.markdown("---")
        st.markdown("#### รายชื่อหมวดหมู่ที่มีอยู่ & จัดการ/ลบ")

        for c_idx, cat_item in enumerate(st.session_state.categories_list):
            cols_c = st.columns([3, 1, 1])
            with cols_c[0]:
                st.write(f"- {cat_item}")
            with cols_c[1]:
                if st.button("✏️ แก้ไข", key=f"edit_cat_{c_idx}"):
                    st.info(f"🔄 อัปเดตหมวดหมู่เรียบร้อยแล้ว")
            with cols_c[2]:
                if st.button("🗑️ ลบ", key=f"del_cat_{c_idx}"):
                    st.session_state.categories_list.remove(cat_item)
                    st.error(f"🗑️ ลบหมวดหมู่ '{cat_item}' ออกจากระบบแล้ว!")
                    st.rerun()

    # --- Tab 4: จัดการ/เพิ่มบริษัทจัดซื้อสินค้า ---
    with tab_manage_supplier:
        st.subheader("จัดการ/เพิ่มบริษัทจัดซื้อสินค้า (Supplier Profile)")

        if "suppliers_list" not in st.session_state:
            st.session_state.suppliers_list = []

        with st.form("form_add_supplier"):
            st.markdown("##### ➕ เพิ่มบริษัทจัดซื้อใหม่")
            sup_name = st.text_input("1. ชื่อบริษัท")
            sup_address = st.text_area("2. ที่อยู่บริษัท")
            sup_tax = st.text_input("3. เลขที่ผู้เสียภาษี")
            sup_contact = st.text_input("4. ข้อมูลติดต่อเซลล์ (ชื่อ, เบอร์โทร, ไลน์ ฯลฯ)")

            submitted_sup = st.form_submit_button("💾 บันทึกบริษัทใหม่")

        if submitted_sup:
            if not sup_name.strip():
                st.error("⚠️ กรุณากรอกชื่อบริษัท")
            else:
                st.session_state.suppliers_list.append({
                    "name": sup_name,
                    "address": sup_address,
                    "tax_id": sup_tax,
                    "contact": sup_contact
                })
                st.success(f"✨ เพิ่มบริษัท '{sup_name}' สำเร็จเรียบร้อยแล้ว!")
                st.rerun()

        st.markdown("---")
        st.markdown("**รายชื่อบริษัทที่จัดซื้อปัจจุบัน:**")

        if not st.session_state.suppliers_list:
            st.info("ยังไม่มีข้อมูลบริษัทจัดซื้อในระบบ")
        else:
            for idx, sup in enumerate(st.session_state.suppliers_list):
                cols_s = st.columns([3, 1.5])
                cols_s[0].write(f"**{idx + 1}. {sup['name']}**\n- ที่อยู่: {sup['address']}\n- เลขผู้เสียภาษี: {sup['tax_id']}\n- ติดต่อเซลล์: {sup['contact']}")
                action_s = cols_s[1].selectbox("จัดการ", ["เลือก", "แก้ไข", "ลบ"], key=f"action_sup_{idx}", label_visibility="collapsed")

                if action_s == "ลบ":
                    st.session_state.suppliers_list.pop(idx)
                    st.success("ลบข้อมูลบริษัทเรียบร้อยแล้ว")
                    st.rerun()
                elif action_s == "แก้ไข":
                    st.session_state[f"edit_mode_sup_{idx}"] = True

                if st.session_state.get(f"edit_mode_sup_{idx}", False):
                    with st.form(f"form_edit_sup_{idx}"):
                        st.markdown(f"##### แก้ไขข้อมูลบริษัท: {sup['name']}")
                        ed_name = st.text_input("1. ชื่อบริษัท", value=sup['name'])
                        ed_addr = st.text_area("2. ที่อยู่บริษัท", value=sup['address'])
                        ed_tax = st.text_input("3. เลขที่ผู้เสียภาษี", value=sup['tax_id'])
                        ed_cont = st.text_input("4. ข้อมูลติดต่อเซลล์", value=sup['contact'])
                        
                        c_ss1, c_ss2 = st.columns(2)
                        with c_ss1:
                            submitted_edit = st.form_submit_button("💾 บันทึกการแก้ไข")
                        with c_ss2:
                            submitted_cancel = st.form_submit_button("❌ ยกเลิก")

                        if submitted_edit:
                            st.session_state.suppliers_list[idx] = {
                                "name": ed_name,
                                "address": ed_addr,
                                "tax_id": ed_tax,
                                "contact": ed_cont
                            }
                            st.session_state[f"edit_mode_sup_{idx}"] = False
                            st.success("✅ แก้ไขข้อมูลบริษัทสำเร็จ")
                            st.rerun()
                            
                        if submitted_cancel:
                            st.session_state[f"edit_mode_sup_{idx}"] = False
                            st.rerun()
                            
                    st.markdown("---")

    st.markdown("---")
# ---------------------------------------------------------
# เมนูที่ 4 (m4): บันทึกรับสินค้าเข้าสต็อก (Stock In)
# ---------------------------------------------------------
elif selected_menu == t_ui["m4"]:
    st.title(f"{t_ui['m4']} - {comp_display_name}")
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
        
        si_search_query = st.text_input("Search Product Code or Name" if lang == "English" else "🔍 พิมพ์รหัสสินค้า (Product Code) หรือชื่อสินค้าเพื่อค้นหา...")
        
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

elif selected_menu == t_ui["m5"]:
    st.title(f"{t_ui['m5']} - {comp_display_name}")
    if len(current_inv) == 0:
        st.warning("No items available.")
    else:
        item_options = current_inv["Item Name"].tolist()
        display_item_options = [translate_item_name(x, lang) for x in item_options]

        with st.form("stock_out_form"):
            so_date = st.date_input("Date", value=datetime.today())
            selected_display_item = st.selectbox("Select Item", display_item_options)
            
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

elif selected_menu == t_ui["m6"]:
    st.title(f"{t_ui['m6']} - {comp_display_name}")
    pr_tab1, pr_tab2 = st.tabs(["📄 1. PR", "📦 2. PO"])

    with pr_tab1:
        st.subheader("Create PR")
        if "temp_pr_cart" not in st.session_state:
            st.session_state["temp_pr_cart"] = []
        st.info("PR system active.")

    with pr_tab2:
        st.subheader("Purchase Orders (PO)")
        st.info("PO system active.")

elif selected_menu == t_ui["m7"]:
    st.title(f"{t_ui['m7']} - {comp_display_name}")
    if len(st.session_state["transaction_history"]) > 0:
        hist_df = st.session_state["transaction_history"].copy()
        if lang == "English":
            hist_df["Item Name"] = hist_df["Item Name"].apply(lambda x: translate_item_name(x, lang))
        st.dataframe(hist_df, use_container_width=True)
    else:
        st.info("No transaction history.")

elif selected_menu == t_ui["m8"]:
    st.title(f"{t_ui['m8']} - {comp_display_name}")
    if len(display_inv) > 0:
        st.dataframe(display_inv, use_container_width=True)
    else:
        st.info("No stock data.")

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
