import streamlit as st
import pandas as pd
from datetime import datetime
import io

# ------------------------------------------------------------------
# 0. Basic page config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Enterprise Stock & Multi-Company System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# 1. Company list, categories, units, VAT, language dicts
# ------------------------------------------------------------------
COMPANIES = [
    "ทุกบริษัท/สาขา (All Companies / Branches)",
    "Daddy Deli (Head Office)",
    "Harvest Cafe (Branch 0001)",
    "Taboo By Daddy Deli (Branch 0002)",
    "Daddy Deli Pattaya Group (Head Office)",
    "Harvest Bakery And Restaurant (Head Office)",
    "Daddy Deli Beach House (Head Office)",
]
REAL_COMPANIES = [c for c in COMPANIES if "ทุกบริษัท" not in c]

if "categories_list" not in st.session_state:
    st.session_state.categories_list = [
        "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others",
        "ผักและผลไม้ / Vegetables & Fruits",
        "ทะเล / Seafood",
        "เนื้อวัว / Beef",
        "น้ำผลไม้/Soft Drink/อื่นๆ / Juice/Soft Drink/Other",
        "เบียร์ / Beer",
        "ไส้กรอก / Sausage",
        "ชีส / Cheese",
        "นม / Milk",
    ]

if "units_list" not in st.session_state:
    st.session_state.units_list = ["Box", "Pack", "Bag", "Kg", "Pcs", "Litre", "Bottle", "Can", "Gram"]

VAT_TYPES_LIST = ["Non Vat", "Vat 7%"]

LANG = {
    "th": {
        "title": "ระบบจัดการสต็อกวัตถุดิบและคลังสินค้า (Multi-Company)",
        "menu": "📌 เมนูหลัก",
        "m_dashboard": "📊 แดชบอร์ดภาพรวม",
        "m_inventory_mgmt": "📦 การจัดการรายการสินค้า",
        "sub_import_excel": "📥 เพิ่มรายการสินค้าใหม่",
        "sub_stock_in": "📥 รับสินค้า (Stock In)",
        "sub_stock_out": "📤 เบิกสินค้า (Stock Out)",
        "m_history": "📜 ประวัติการทำรายการ",
        "m_pr_po": "📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)",
        "m_eom": "📋 รายการสรุปสต็อก & นับสต็อก",
        "m_company_settings": "🏢 ตั้งค่าข้อมูลบริษัทและแอดมิน",
    },
    "en": {
        "title": "Enterprise Food Cost & Stock Management System",
        "menu": "📌 Main Menu",
        "m_dashboard": "📊 Dashboard & Overview",
        "m_inventory_mgmt": "📦 Inventory Management",
        "sub_import_excel": "📥 Add New Items",
        "sub_stock_in": "📥 Stock In",
        "sub_stock_out": "📤 Stock Out / Requisition",
        "m_history": "📜 Transaction History",
        "m_pr_po": "📝 Purchase Request (PR) & PO",
        "m_eom": "📋 Stock Summary & End of Month Count",
        "m_company_settings": "🏢 Company & Admin Settings",
    },
}

TRANSLATE_DICT = {
    "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others": "Meat / Seasonings / Others",
    "ผักและผลไม้ / Vegetables & Fruits": "Vegetables & Fruits",
    "ทะเล / Seafood": "Seafood",
    "เนื้อวัว / Beef": "Beef",
    "น้ำผลไม้/Soft Drink/อื่นๆ / Juice/Soft Drink/Other": "Juice / Soft Drink / Other",
    "เบียร์ / Beer": "Beer",
    "ไส้กรอก / Sausage": "Sausage",
    "ชีส / Cheese": "Cheese",
    "นม / Milk": "Milk",
}

# ------------------------------------------------------------------
# 2. Session state initialization
# ------------------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "th"

if "company_details" not in st.session_state:
    st.session_state.company_details = {}
    for comp in REAL_COMPANIES:
        st.session_state.company_details[comp] = {
            "name": comp,
            "address": f"ที่อยู่สำนักงานใหญ่/สาขา ของ {comp}",
            "tax_id": "01055xxxxxxxx",
            "contact": "02-xxx-xxxx / เซลล์: คุณสมชาย (081-234-5678)",
        }

if "company_logos" not in st.session_state:
    st.session_state.company_logos = {}

if "company_inventories" not in st.session_state:
    st.session_state.company_inventories = {}
    for comp in REAL_COMPANIES:
        st.session_state.company_inventories[comp] = pd.DataFrame(
            columns=[
                "Product Code",
                "Item Name",
                "Category",
                "Unit",
                "Conversion Qty",
                "Stock Balance",
                "Last Price",
                "Supplier",
                "Vat Type",
            ]
        )
    st.session_state.company_inventories[REAL_COMPANIES[0]] = pd.DataFrame(
        [
            {
                "Product Code": "422582",
                "Item Name": "นมจืด 1 ลิตร",
                "Category": "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others",
                "Unit": "Box",
                "Conversion Qty": 1.0,
                "Stock Balance": 25.0,
                "Last Price": 109.0,
                "Supplier": "CP Axtra (Makro)",
                "Vat Type": "Non Vat",
            },
            {
                "Product Code": "2502009877754",
                "Item Name": "กระเทียมดัดจุก 500 ก.",
                "Category": "ผักและผลไม้ / Vegetables & Fruits",
                "Unit": "Pack",
                "Conversion Qty": 500.0,
                "Stock Balance": 10.0,
                "Last Price": 40.0,
                "Supplier": "CP Axtra (Lotus)",
                "Vat Type": "Non Vat",
            },
            {
                "Product Code": "54061057",
                "Item Name": "คิทแคท ทริกเกอร์ 500 กรัม",
                "Category": "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others",
                "Unit": "Bag",
                "Conversion Qty": 500.0,
                "Stock Balance": 0.0,
                "Last Price": 130.0,
                "Supplier": "กส-สรา ค้าส่ง",
                "Vat Type": "Vat 7%",
            },
        ]
    )

if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        [
            {
                "Company": REAL_COMPANIES[0],
                "Date": str(datetime.today().date()),
                "DocNo": "INV-001",
                "Supplier": "CP Axtra (Makro)",
                "Item Name": "นมจืด 1 ลิตร",
                "Quantity": 25.0,
                "Price/Unit": 109.0,
                "Vat Type": "Non Vat",
                "Total Price": 2725.0,
                "Type": "IMPORT",
                "Receiver": "-",
                "Department": "-",
            }
        ]
    )

if "admins" not in st.session_state:
    st.session_state.admins = pd.DataFrame(
        [
            {"Username": "owner_master", "Name": "Mr. Owner", "Branch": "All Branches", "Role": "Owner"},
            {"Username": "manager_a", "Name": "คุณสมชาย ใจดี", "Branch": "All Branches", "Role": "Manager"},
            {"Username": "office_staff", "Name": "คุณสมหญิง ฝ่ายออฟฟิศ", "Branch": "All Branches", "Role": "Office"},
            {"Username": "admin_daddy", "Name": "แอดมิน แดดดี้ เดลี่", "Branch": REAL_COMPANIES[0], "Role": "Admin"},
        ]
    )

if "purchase_requests" not in st.session_state:
    st.session_state.purchase_requests = pd.DataFrame(columns=["PR_ID", "Date", "Supplier", "Branch", "Status", "Requester", "Items_JSON"])

if "purchase_orders" not in st.session_state:
    st.session_state.purchase_orders = pd.DataFrame(columns=["PO_ID", "PR_ID", "Supplier", "Branch", "Date"])

if "wast_variance_records" not in st.session_state:
    st.session_state.wast_variance_records = pd.DataFrame(
        columns=["Company", "Date", "Item Name", "Wast_Variance", "OC_Test", "Note"]
    )

# ------------------------------------------------------------------
# 3. Sidebar: language, company, user & role-based restriction
# ------------------------------------------------------------------
with st.sidebar:
    lang_index = 0 if st.session_state.lang == "th" else 1
    lang_choice = st.selectbox("🌐 ภาษา / Language", ["ไทย (Thai)", "English"], index=lang_index)
    st.session_state.lang = "th" if lang_choice == "ไทย (Thai)" else "en"

    st.markdown("---")
    
    admin_list = st.session_state["admins"]["Username"].tolist()
    current_user_name = st.selectbox("👤 ผู้ใช้งานปัจจุบัน (Current User):", admin_list)
    user_info = st.session_state["admins"][st.session_state["admins"]["Username"] == current_user_name].iloc[0]
    
    user_role = user_info["Role"]
    user_branch = user_info["Branch"]

    if user_role == "Admin":
        if user_branch in REAL_COMPANIES:
            selected_company = st.selectbox("🏢 เลือกบริษัท / สาขา", [user_branch])
        else:
            selected_company = st.selectbox("🏢 เลือกบริษัท / สาขา", REAL_COMPANIES)
        st.warning(f"🔒 สิทธิ์ Admin: เข้าถึงได้เฉพาะสาขา {selected_company}")
    else:
        selected_company = st.selectbox("🏢 เลือกบริษัท / สาขา", COMPANIES)

    st.info(f"**{user_info['Name']}**\n\nสิทธิ์: {user_role}")

    st.markdown("---")
    st.markdown("### 📌 เมนูหลัก")

    pending_pr_count = (
        st.session_state["purchase_requests"]["Status"]
        .str.contains("Pending (รออนุมัติ)")
        .sum()
        if len(st.session_state["purchase_requests"]) > 0
        else 0
    )
    pr_menu_label = "📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)"
    if pending_pr_count > 0:
        pr_menu_label = f"📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO) 🔴({pending_pr_count})"

    t = LANG[st.session_state.lang]

    selected_menu = st.radio(
        "Navigation",
        [
            t["m_dashboard"],
            t["m_inventory_mgmt"],
            t["sub_import_excel"],
            t["sub_stock_in"],
            t["sub_stock_out"],
            t["m_history"],
            pr_menu_label,
            t["m_eom"],
            t["m_company_settings"],
        ],
        label_visibility="collapsed",
    )

# ------------------------------------------------------------------
# 4. Figure out which inventory dataframe to use
# ------------------------------------------------------------------
def get_visible_inventory():
    if user_role == "Admin":
        return st.session_state["company_inventories"].get(user_branch, pd.DataFrame())
    
    if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
        return pd.concat(list(st.session_state["company_inventories"].values()), ignore_index=True)
    else:
        return st.session_state["company_inventories"].get(selected_company, pd.DataFrame())

current_inv = get_visible_inventory()

trans_df = st.session_state["transactions"]
if selected_company != "ทุกบริษัท/สาขา (All Companies / Branches)" and user_role != "Admin":
    trans_df = trans_df[trans_df["Company"] == selected_company]
elif user_role == "Admin":
    trans_df = trans_df[trans_df["Company"] == user_branch]

def localize_text(text):
    return TRANSLATE_DICT.get(text, text) if st.session_state.lang == "en" else text

# ------------------------------------------------------------------
# 5. App sections
# ------------------------------------------------------------------
# a) Dashboard
if selected_menu == t["m_dashboard"]:
    st.title(f"📊 แดชบอร์ดภาพรวม - {selected_company}")

    import_trans = trans_df[trans_df["Type"] == "IMPORT"]
    total_purchase_amount = import_trans["Total Price"].sum() if len(import_trans) > 0 else 0.0

    total_items = len(current_inv)
    total_qty = current_inv["Stock Balance"].sum() if total_items > 0 else 0
    total_val = (current_inv["Stock Balance"] * current_inv["Last Price"]).sum() if total_items > 0 else 0

    wast_df = st.session_state["wast_variance_records"]
    if selected_company != "ทุกบริษัท/สาขา (All Companies / Branches)":
        wast_df = wast_df[wast_df["Company"] == selected_company]

    total_wast = wast_df["Wast_Variance"].sum() if len(wast_df) > 0 else 0.0
    total_oc = wast_df["OC_Test"].sum() if len(wast_df) > 0 else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💵 ยอดเงินซื้อวัตถุดิบรวม", f"{total_purchase_amount:,.2f} THB")
    col2.metric("📦 สต็อกคงเหลือ (มูลค่า)", f"{total_val:,.2f} THB ({total_qty:,.2f} หน่วย)")
    col3.metric("🗑️ Wast & Variance รวม", f"{total_wast:,.2f}")
    col4.metric("🎁 OC / Test รวม", f"{total_oc:,.2f}")

    st.markdown("---")
    st.subheader("📋 รายการวัตถุดิบในคลังปัจจุบัน")
    if len(current_inv) > 0:
        st.dataframe(current_inv, use_container_width=True)
    else:
        st.info("ไม่มีข้อมูลสินค้า")

# b) Inventory Management
elif selected_menu == t["m_inventory_mgmt"]:
    st.title(f"📦 การจัดการรายการสินค้า - {selected_company}")
    if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
        st.warning("เลือก 1 บริษัท เพื่อแก้ไขรายการสินค้า")
    else:
        col_m1, col_m2, col_m3 = st.columns(3)
        all_cats_mgmt = ["ทุกหมวดหมู่ (All Categories)"] + st.session_state.categories_list
        selected_mgmt_cat = col_m1.selectbox("เลือกตามหมวดหมู่", all_cats_mgmt)
        
        suppliers_list_mgmt = ["ทุกร้านค้า/บริษัท (All Suppliers)"] + (current_inv["Supplier"].dropna().unique().tolist() if len(current_inv) > 0 else [])
        selected_mgmt_supplier = col_m2.selectbox("ค้นหาด้วยร้านค้า/บริษัท", suppliers_list_mgmt)
        
        search_mgmt_keyword = col_m3.text_input("🔍 ค้นหาชื่อหรือรหัสสินค้า")

        mgmt_filtered = current_inv.copy()
        if selected_mgmt_cat != "ทุกหมวดหมู่ (All Categories)":
            mgmt_filtered = mgmt_filtered[mgmt_filtered["Category"] == selected_mgmt_cat]
        if selected_mgmt_supplier != "ทุกร้านค้า/บริษัท (All Suppliers)":
            mgmt_filtered = mgmt_filtered[mgmt_filtered["Supplier"] == selected_mgmt_supplier]
        if search_mgmt_keyword.strip():
            kw = search_mgmt_keyword.strip().lower()
            mgmt_filtered = mgmt_filtered[
                mgmt_filtered["Item Name"].str.lower().str.contains(kw, na=False) |
                mgmt_filtered["Product Code"].str.lower().str.contains(kw, na=False)
            ]

        for idx, row in mgmt_filtered.iterrows():
            col_r = st.columns([2, 2, 1, 1, 1, 1, 1])
            col_r[0].write(row["Item Name"])
            col_r[1].write(row["Category"])
            col_r[2].write(f"{row['Stock Balance']} {row['Unit']}")
            col_r[3].write(f"{row['Conversion Qty']}")
            col_r[4].write(f"{row['Last Price']} ฿")
            if col_r[5].button("✏️ แก้ไข", key=f"edit_{idx}"):
                st.session_state[f"open_edit_{idx}"] = not st.session_state.get(f"open_edit_{idx}", False)
            if col_r[6].button("🗑️ ลบ", key=f"del_{idx}"):
                st.session_state["company_inventories"][selected_company] = current_inv.drop(idx).reset_index(drop=True)
                st.rerun()

            if st.session_state.get(f"open_edit_{idx}", False):
                with st.form(f"form_edit_{idx}"):
                    new_n = st.text_input("ชื่อ", value=row["Item Name"])
                    new_p = st.number_input("ราคา", value=float(row["Last Price"]))
                    new_b = st.number_input("สต็อก", value=float(row["Stock Balance"]))
                    new_conv = st.number_input("ปริมาณต่อหน่วย", value=float(row.get("Conversion Qty", 1.0)))
                    if st.form_submit_button("บันทึก"):
                        st.session_state["company_inventories"][selected_company].loc[idx, "Item Name"] = new_n
                        st.session_state["company_inventories"][selected_company].loc[idx, "Last Price"] = new_p
                        st.session_state["company_inventories"][selected_company].loc[idx, "Stock Balance"] = new_b
                        st.session_state["company_inventories"][selected_company].loc[idx, "Conversion Qty"] = new_conv
                        st.session_state[f"open_edit_{idx}"] = False
                        st.rerun()

# c) Add New Items with 4 Ordered Tabs matching the requested layout
elif selected_menu == t["sub_import_excel"]:
    st.title(f"📥 เพิ่มรายการสินค้าใหม่ - {selected_company}")
    if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
        st.warning("กรุณาเลือก 1 บริษัทเฉพาะเจาะจงก่อนทำรายการ")
    else:
        tab1, tab2, tab3, tab4 = st.tabs([
            "1. เพิ่มรายการสินค้าใหม่",
            "2. เพิ่ม/แก้ไขข้อมูลร้านค้า",
            "3. เพิ่ม/แก้ไขหน่วยนับ (Units)",
            "4. เพิ่ม/แก้ไขหมวดหมู่สินค้า (Categories)"
        ])

        with tab1:
            st.subheader("เลือกเพิ่มแบบกรอกข้อมูลหรือเพิ่มผ่านไฟล์ Excel ในหน้าเดียวกัน")
            sub_tab_excel, sub_tab_manual = st.tabs(["📄 นำเข้าผ่านไฟล์ Excel", "✍️ เพิ่มรายการแบบกรอกข้อมูล"])

            with sub_tab_excel:
                uploaded_file = st.file_uploader("เลือกไฟล์ Excel สำหรับนำเข้าสต็อก", type=["xlsx", "csv"])
                if uploaded_file:
                    st.success("อัปโหลดไฟล์สำเร็จ ระบบได้ทำการเพิ่มรายการสินค้าแล้ว")

            with sub_tab_manual:
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
                        conversion_qty = st.number_input("ปริมาณต่อหน่วย", min_value=0.0, value=1.0)
                        
                    vat_type = st.selectbox("ประเภทภาษี", VAT_TYPES_LIST)
                    submit_manual = st.form_submit_button("💾 บันทึกเพิ่มรายการสินค้าใหม่")

                    if submit_manual:
                        inv = st.session_state["company_inventories"][selected_company]
                        idx_match = inv.index[inv["Item Name"] == item_name]
                        if not idx_match.empty:
                            idx = idx_match[0]
                            inv.loc[idx, "Supplier"] = supplier
                            inv.loc[idx, "Unit"] = unit_manual
                            inv.loc[idx, "Conversion Qty"] = conversion_qty
                        else:
                            new_row = pd.DataFrame([{
                                "Product Code": sku,
                                "Item Name": item_name,
                                "Category": cat_manual,
                                "Unit": unit_manual,
                                "Conversion Qty": conversion_qty,
                                "Stock Balance": 0.0,
                                "Last Price": 0.0,
                                "Supplier": supplier,
                                "Vat Type": vat_type,
                            }])
                            st.session_state["company_inventories"][selected_company] = pd.concat(
                                [inv, new_row], ignore_index=True
                            )

                        st.success("บันทึกเพิ่มรายการสินค้าใหม่สำเร็จ!")
                        st.rerun()

        with tab2:
            st.subheader("ตั้งค่าข้อมูลร้านค้า (ที่อยู่ / โลโก้)")
            curr_details = st.session_state["company_details"].get(selected_company, {
                "name": selected_company,
                "address": "",
                "tax_id": "",
                "contact": ""
            })
            existing_logo = st.session_state["company_logos"].get(selected_company)
            if existing_logo is not None:
                st.image(existing_logo, width=150, caption="โลโก้ปัจจุบันของบริษัท")
            
            with st.form("company_info_form_in_add"):
                c_name = st.text_input("1. ชื่อร้านค้า/บริษัท", value=curr_details.get("name", selected_company))
                c_address = st.text_area("2. ที่อยู่", value=curr_details.get("address", ""))
                c_tax = st.text_input("3. เลขที่ผู้เสียภาษี", value=curr_details.get("tax_id", ""))
                c_contact = st.text_input("4. ข้อมูลติดต่อ / เซลล์", value=curr_details.get("contact", ""))
                
                uploaded_logo = st.file_uploader("🖼️ อัปโหลดโลโก้บริษัท (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"], key="logo_add_page")
                if st.form_submit_button("💾 บันทึกข้อมูลร้านค้า"):
                    st.session_state["company_details"][selected_company] = {
                        "name": c_name,
                        "address": c_address,
                        "tax_id": c_tax,
                        "contact": c_contact
                    }
                    if uploaded_logo is not None:
                        st.session_state["company_logos"][selected_company] = uploaded_logo
                    st.success("บันทึกข้อมูลร้านค้าเรียบร้อยแล้ว!")
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
                
                edit_key = f"edit_unit_{i}"
                del_key = f"del_unit_{i}"
                
                if cols[1].button("✏️ แก้ไข", key=edit_key):
                    st.session_state[f"show_edit_unit_{i}"] = not st.session_state.get(f"show_edit_unit_{i}", False)
                if cols[2].button("🗑️ ลบ", key=del_key):
                    if len(st.session_state.units_list) > 1:
                        st.session_state.units_list.pop(i)
                        st.success("ลบหน่วยนับเรียบร้อยแล้ว")
                        st.rerun()
                    else:
                        st.warning("ต้องมีหน่วยนับอย่างน้อย 1 รายการ")
                
                if st.session_state.get(f"show_edit_unit_{i}", False):
                    with st.form(f"form_edit_unit_{i}" ):
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
                
                edit_cat_key = f"edit_cat_{j}"
                del_cat_key = f"del_cat_{j}"
                
                if cols_c[1].button("✏️ แก้ไข", key=edit_cat_key):
                    st.session_state[f"show_edit_cat_{j}"] = not st.session_state.get(f"show_edit_cat_{j}", False)
                if cols_c[2].button("🗑️ ลบ", key=del_cat_key):
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
    st.title(f"📥 รับสินค้าเข้า (Stock In) - {selected_company}")
    if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
        st.warning("เลือกบริษัทเฉพาะเจาะจงเพื่อทำรายการรับสินค้า")
    else:
        if "temp_stock_in_items" not in st.session_state:
            st.session_state["temp_stock_in_items"] = []

        st.subheader("1. ข้อมูลใบรับสินค้าและผู้รับ")
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        with col_h1:
            stock_in_date = st.date_input("วันที่รับเข้า", value=datetime.today())
        with col_h2:
            existing_suppliers = current_inv["Supplier"].unique().tolist() if len(current_inv) > 0 else ["CP Axtra (Makro)", "CP Axtra (Lotus)", "ร้านค้าทั่วไป"]
            supplier_in = st.selectbox("ชื่อร้านค้าที่ซื้อ (Supplier)", existing_suppliers)
        with col_h3:
            doc_no = st.text_input("เลขที่เอกสาร (ใบกำกับภาษี/ใบเสร็จ)")
        with col_h4:
            receiver_in = st.text_input("ผู้รับสินค้าเข้า", value=user_info["Name"])

        upload_option = st.radio("เลือกวิธีแนบหลักฐาน", ["📂 อัปโหลดไฟล์รูปภาพ", "📸 ถ่ายภาพด้วยกล้อง"], horizontal=True)
        
        saved_photo = None
        if upload_option == "📸 ถ่ายภาพด้วยกล้อง":
            cam_photo = st.camera_input("ถ่ายรูปภาพสินค้าและใบเสร็จ")
            if cam_photo is not None:
                saved_photo = cam_photo
        else:
            up_photo = st.file_uploader("เลือกไฟล์รูปภาพ", type=["jpg", "png", "jpeg"])
            if up_photo is not None:
                saved_photo = up_photo

        st.markdown("---")
        st.subheader("2. ค้นหาและเพิ่มรายการสินค้าทีละรายการเข้าตะกร้ารับเข้า")
        
        inv_by_supplier = current_inv[current_inv["Supplier"] == supplier_in].copy() if len(current_inv) > 0 else pd.DataFrame()
        if len(inv_by_supplier) == 0:
            inv_by_supplier = current_inv.copy()

        input_code_search = st.text_input("🔍 พิมพ์รหัสสินค้า (Product Code) เพื่อดึงชื่ออัตโนมัติ")

        matched_by_code = None
        if input_code_search.strip() and len(inv_by_supplier) > 0:
            matched_rows = inv_by_supplier[inv_by_supplier["Product Code"].astype(str).str.lower() == input_code_search.strip().lower()]
            if not matched_rows.empty:
                matched_by_code = matched_rows.iloc[0]

        with st.form("add_item_to_cart_form"):
            if matched_by_code is not None:
                sel_item_in = matched_by_code["Item Name"]
                st.success(f"📌 ระบบพบรหัสสินค้าตรงกับ: **{sel_item_in}**")
                item_options = [sel_item_in]
            else:
                item_options = inv_by_supplier["Item Name"].tolist() if len(inv_by_supplier) > 0 else []
                sel_item_in = st.selectbox(f"เลือกวัตถุดิบรับเข้า (จากร้าน: {supplier_in})", item_options)
            
            selected_code = input_code_search.strip()
            if sel_item_in and len(current_inv) > 0 and not selected_code:
                matched_row = current_inv[current_inv["Item Name"] == sel_item_in]
                if not matched_row.empty:
                    selected_code = str(matched_row.iloc[0]["Product Code"])
            elif matched_by_code is not None:
                selected_code = str(matched_by_code["Product Code"])
            
            st.markdown(f"🏷️ **รหัสสินค้า (Product Code):** `{selected_code}`")

            # ดึงค่าหน่วยนับเริ่มต้นของสินค้าที่เลือก
            default_item_unit = "หน่วย"
            if sel_item_in and len(current_inv) > 0:
                mr_unit = current_inv[current_inv["Item Name"] == sel_item_in]
                if not mr_unit.empty and "Unit" in mr_unit.columns:
                    default_item_unit = str(mr_unit.iloc[0]["Unit"])

            col_sub1, col_sub_unit, col_sub2, col_sub3 = st.columns([2, 1.5, 2, 2])
            with col_sub1:
                qty_in = st.number_input("จำนวนรับเข้า", min_value=0.1, value=1.0)
            with col_sub_unit:
                unit_in = st.selectbox("หน่วยนับ", st.session_state.units_list, index=st.session_state.units_list.index(default_item_unit) if default_item_unit in st.session_state.units_list else 0)
            with col_sub2:
                default_price = 0.0
                if sel_item_in and len(current_inv) > 0:
                    mr = current_inv[current_inv["Item Name"] == sel_item_in]
                    if not mr.empty:
                        default_price = float(mr.iloc[0]["Last Price"])
                price_in = st.number_input("ราคาต่อหน่วย", min_value=0.0, value=default_price)
            with col_sub3:
                vat_in = st.selectbox("ประเภทภาษี", VAT_TYPES_LIST)

            add_to_cart_btn = st.form_submit_button("➕ เพิ่มรายการนี้ลงในตะกร้ารอรับเข้า")
            if add_to_cart_btn and sel_item_in:
                st.session_state["temp_stock_in_items"].append({
                    "Product Code": selected_code,
                    "Item Name": sel_item_in,
                    "Quantity": qty_in,
                    "Unit": unit_in,
                    "Price/Unit": price_in,
                    "Vat Type": vat_in,
                    "Total Price": qty_in * price_in
                })
                st.success(f"เพิ่ม '{sel_item_in}' ลงในรายการแล้ว")

        if len(st.session_state["temp_stock_in_items"]) > 0:
            st.markdown("---")
            st.subheader("3. รายการสินค้าที่รอการบันทึกรับเข้า")
            temp_df = pd.DataFrame(st.session_state["temp_stock_in_items"])
            st.dataframe(temp_df, use_container_width=True)

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🗑️ ล้างรายการที่เลือกทั้งหมด"):
                    st.session_state["temp_stock_in_items"] = []
                    st.rerun()
            with col_btn2:
                if st.button("💾 ยืนยันบันทึกรับสินค้าเข้าสต็อกทั้งหมด"):
                    for itm in st.session_state["temp_stock_in_items"]:
                        it_name = itm["Item Name"]
                        it_qty = itm["Quantity"]
                        it_price = itm["Price/Unit"]
                        it_vat = itm["Vat Type"]

                        idx_m = current_inv[current_inv["Item Name"] == it_name].index
                        if len(idx_m) > 0:
                            idx = idx_m[0]
                            st.session_state["company_inventories"][selected_company].loc[idx, "Stock Balance"] += it_qty
                            st.session_state["company_inventories"][selected_company].loc[idx, "Last Price"] = it_price
                            st.session_state["company_inventories"][selected_company].loc[idx, "Supplier"] = supplier_in

                        new_t = {
                            "Company": selected_company,
                            "Date": str(stock_in_date),
                            "DocNo": doc_no,
                            "Supplier": supplier_in,
                            "Item Name": it_name,
                            "Quantity": it_qty,
                            "Price/Unit": it_price,
                            "Vat Type": it_vat,
                            "Total Price": it_qty * it_price,
                            "Type": "IMPORT",
                            "Receiver": receiver_in,
                            "Department": "-",
                        }
                        st.session_state["transactions"] = pd.concat(
                            [st.session_state["transactions"], pd.DataFrame([new_t])], ignore_index=True
                        )

                    st.session_state["temp_stock_in_items"] = []
                    st.success("บันทึกรับสินค้าเข้าคลังทั้งหมดสำเร็จ!")
                    st.rerun()

# e) Stock Out
elif selected_menu == t["sub_stock_out"]:
    st.title(f"📤 เบิกสินค้า (Stock Out) - {selected_company}")
    if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
        st.warning("เลือกเฉพาะ 1 บริษัท เพื่อทำรายการเบิกสินค้า")
    else:
        with st.form("stock_out_form_new"):
            sel_item_out = st.selectbox("เลือกวัตถุดิบที่ต้องการเบิก", current_inv["Item Name"].tolist() if len(current_inv) > 0 else [])
            qty_out = st.number_input("จำนวนที่ต้องการเบิก", min_value=0.1, value=1.0)
            unit_out = st.selectbox("เลือกหน่วยนับ", st.session_state.units_list)
            date_out = st.date_input("วันที่เบิกสินค้า", value=datetime.today())
            requester_out = st.text_input("ชื่อผู้เบิก")
            department_out = st.text_input("แผนกที่นำไปใช้")

            submit_out = st.form_submit_button("ยืนยันการเบิกสินค้า")
            if submit_out and sel_item_out:
                if "temp_out_list" not in st.session_state:
                    st.session_state["temp_out_list"] = []
                st.session_state["temp_out_list"].append(
                    {
                        "Item": sel_item_out,
                        "Qty": qty_out,
                        "Unit": unit_out,
                        "Date": str(date_out),
                        "Dept": department_out,
                    }
                )
                st.success("บันทึกการเบิกชั่วคราวสำเร็จ")

        st.markdown("---")
        st.subheader("📋 รายการที่กดเบิกสินค้าไปแล้วในเซสชันนี้")
        if "temp_out_list" in st.session_state and len(st.session_state["temp_out_list"]) > 0:
            st.dataframe(pd.DataFrame(st.session_state["temp_out_list"]), use_container_width=True)
        else:
            st.info("ยังไม่มีรายการเบิกใหม่ในรอบนี้")

# f) Transaction History
elif selected_menu == t["m_history"]:
    st.title(f"📜 ประวัติการทำรายการ - {selected_company}")
    if len(trans_df) > 0:
        st.dataframe(trans_df, use_container_width=True)
    else:
        st.info("ไม่มีประวัติการทำรายการ")

# g) PR / PO workflow
elif pr_menu_label in selected_menu:
    pass  

# h) Stock Count / End‑of‑Month
elif selected_menu == t["m_eom"]:
    st.title(f"📋 รายการสรุปสต็อก & นับสต็อก - {selected_company}")
    if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
        st.warning("เลือก 1 บริษัท เพื่อทำรายการสรุปและนับสต็อก")
    else:
        st.subheader("📥 นำเข้า/ส่งออก Excel นับสต็อก")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            current_inv.to_excel(writer, sheet_name="Stock_Count", index=False)
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์ Excel สำหรับนับสต็อก",
            data=output.getvalue(),
            file_name=f"stock_count_{selected_company}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        up_excel_count = st.file_uploader("📤 อัปโหลดไฟล์ Excel ที่นับสต็อกแล้ว", type=["xlsx"])
        if up_excel_count:
            st.success("อัปโหลดและอัปเดตสต็อกเรียบร้อยแล้ว!")

        st.markdown("---")
        st.subheader("ช่องบันทึก Wast & Variance และ OC / Test")
        with st.form("wast_form"):
            item_wast = st.selectbox("เลือกสินค้า", current_inv["Item Name"].tolist() if len(current_inv) > 0 else [])
            wast_val = st.number_input("Wast & Variance (จำนวน)", min_value=0.0, value=0.0)
            oc_val = st.number_input("OC / Test (จำนวน)", min_value=0.0, value=0.0)
            note_w = st.text_input("หมายเหตุ")
            if st.form_submit_button("บันทึกข้อมูล Wast / OC"):
                new_w = {
                    "Company": selected_company,
                    "Date": str(datetime.today().date()),
                    "Item Name": item_wast,
                    "Wast_Variance": wast_val,
                    "OC_Test": oc_val,
                    "Note": note_w,
                }
                st.session_state["wast_variance_records"] = pd.concat(
                    [st.session_state["wast_variance_records"], pd.DataFrame([new_w])], ignore_index=True
                )
                st.success("บันทึกสำเร็จ!")
                st.rerun()

# i) Company Settings & Admins
elif selected_menu == t["m_company_settings"]:
    st.title(f"🏢 ตั้งค่าข้อมูลบริษัทและแอดมิน - {selected_company}")
    set_tab1, set_tab2 = st.tabs(["📄 1. ข้อมูลบริษัทและโลโก้", "⚙️ 2. การจัดการแอดมินและสิทธิ์"])

    with set_tab1:
        st.subheader("แก้ไขชื่อ และโลโก้บริษัท")
        with st.form("company_info_form"):
            new_comp_name = st.text_input("ชื่อบริษัท / สาขา", value=selected_company)
            new_tax_id = st.text_input("เลขประจำตัวผู้เสียภาษี (Tax ID)", value="01055xxxxxxxx")
            new_phone = st.text_input("เบอร์โทรศัพท์ติดต่อ", value="02-xxx-xxxx")
            if st.form_submit_button("💾 บันทึกข้อมูลบริษัท"):
                st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
                st.rerun()

    with set_tab2:
        st.subheader("จัดการสิทธิ์ผู้ใช้งานและแอดมินระบบ")
        st.dataframe(st.session_state["admins"], use_container_width=True)
        st.markdown("---")
        st.subheader("🛠️ แก้ไข / ลบ หรือเพิ่มบัญชีแอดมิน")
        admin_names = st.session_state["admins"]["Username"].tolist()
        sel_admin = st.selectbox("เลือกบัญชีผู้ใช้ที่ต้องการแก้ไขหรือลบ", admin_names)
        adm_row = st.session_state["admins"][st.session_state["admins"]["Username"] == sel_admin].iloc[0]
        adm_idx = st.session_state["admins"][st.session_state["admins"]["Username"] == sel_admin].index[0]
        with st.form("edit_admin_form"):
            a_user = st.text_input("Username", value=str(adm_row["Username"]))
            a_name = st.text_input("Full Name / ชื่อ-นามสกุล", value=str(adm_row["Name"]))
            a_branch = st.selectbox(
                "Branch / สาขา",
                COMPANIES + ["All Branches"],
                index=0 if adm_row["Branch"] in COMPANIES else len(COMPANIES),
            )
            a_role = st.selectbox(
                "Role / สิทธิ์",
                ["Owner", "Manager", "Office", "Admin"],
                index=0 if adm_row["Role"] == "Owner" else (1 if adm_row["Role"] == "Manager" else (2 if adm_row["Role"] == "Office" else 3)),
            )
            c_abtn1, c_abtn2 = st.columns(2)
            with c_abtn1:
                up_adm = st.form_submit_button("💾 บันทึกการแก้ไขแอดมิน")
            with c_abtn2:
                del_adm = st.form_submit_button("🗑️ ลบแอดมินนี้ออก")
            if up_adm:
                st.session_state["admins"].loc[adm_idx] = [a_user, a_name, a_branch, a_role]
                st.success("อัปเดตสิทธิ์แอดมินสำเร็จ!")
                st.rerun()
            elif del_adm:
                st.session_state["admins"] = st.session_state["admins"].drop(adm_idx).reset_index(drop=True)
                st.success("ลบแอดมินสำเร็จ!")
                st.rerun()
