elif selected_menu == t_ui["m3"]:
    st.title(f"{t_ui['m3']} - {comp_display_name}")
    st.markdown("กรอกข้อมูลเพื่อเพิ่มรายการสินค้าใหม่เข้าสู่ระบบสต็อกของสาขานี้ หรือจัดการข้อมูลพื้นฐาน")

    tab_add_item, tab_manage_unit, tab_manage_cat, tab_manage_supplier = st.tabs([
        "➕ เพิ่มสินค้าใหม่", 
        "📏 จัดการหน่วยนับ", 
        "🏷️ จัดการหมวดหมู่สินค้า", 
        "🏢 จัดการ/เพิ่มบริษัทที่จัดซื้อสินค้า"
    ])

    with tab_add_item:
        with st.form("add_new_item_form"):
            new_code = st.text_input("รหัสสินค้า (Product Code)")
            new_name = st.text_input("ชื่อสินค้า (Item Name)")
            
            # แปลงเป็น Dropdown ดึงรายชื่อบริษัทจาก suppliers_list (ถ้ามี) หรือใช้ค่าเริ่มต้น
            sup_options = [s["name"] for s in st.session_state.get("suppliers_list", [])]
            if not sup_options:
                sup_options = ["Makro", "Gourmet Market"]
            new_supplier = st.selectbox("1. ค้นหาตามชื่อร้านค้า / Supplier", sup_options)
            
            # แปลงหมวดหมู่สินค้าให้ดึงจาก st.session_state.categories_list แบบ Dropdown
            new_category = st.selectbox("2. ค้นหาตามหมวดหมู่", st.session_state.categories_list)
            
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

    with tab_manage_unit:
        st.subheader("จัดการหน่วยนับ (Units)")
        new_unit_input = st.text_input("เพิ่มหน่วยนับใหม่", key="input_new_unit_tab")
        if st.button("➕ เพิ่มหน่วยนับ", key="btn_add_unit_tab"):
            if new_unit_input and new_unit_input not in st.session_state.units_list:
                st.session_state.units_list.append(new_unit_input)
                st.success(f"เพิ่มหน่วยนับ '{new_unit_input}' สำเร็จ")
                st.rerun()

        st.markdown("---")
        st.markdown("**รายการหน่วยนับปัจจุบัน:**")
        for idx, unit_item in enumerate(st.session_state.units_list):
            cols_u = st.columns([3, 1.5])
            cols_u[0].write(f"{idx + 1}. {unit_item}")
            action_u = cols_u[1].selectbox("จัดการ", ["เลือก", "แก้ไข", "ลบ"], key=f"action_unit_{idx}", label_visibility="collapsed")
            
            if action_u == "ลบ":
                st.session_state.units_list.pop(idx)
                st.success(f"ลบหน่วยนับ '{unit_item}' เรียบร้อยแล้ว")
                st.rerun()
            elif action_u == "แก้ไข":
                st.session_state[f"edit_mode_unit_{idx}"] = True

            if st.session_state.get(f"edit_mode_unit_{idx}", False):
                with st.form(f"form_edit_unit_{idx}"):
                    edited_u = st.text_input("แก้ไขชื่อหน่วยนับ", value=unit_item)
                    c_su1, c_su2 = st.columns(2)
                    if c_su1.form_submit_button("บันทึก"):
                        st.session_state.units_list[idx] = edited_u
                        st.session_state[f"edit_mode_unit_{idx}"] = False
                        st.success("แก้ไขสำเร็จ")
                        st.rerun()
                    if c_su2.form_submit_button("ยกเลิก"):
                        st.session_state[f"edit_mode_unit_{idx}"] = False
                        st.rerun()

    with tab_manage_cat:
        st.subheader("จัดการหมวดหมู่สินค้า (Categories)")
        new_cat_input = st.text_input("เพิ่มหมวดหมู่ใหม่", key="input_new_cat_tab")
        if st.button("➕ เพิ่มหมวดหมู่", key="btn_add_cat_tab"):
            if new_cat_input and new_cat_input not in st.session_state.categories_list:
                st.session_state.categories_list.append(new_cat_input)
                st.success(f"เพิ่มหมวดหมู่ '{new_cat_input}' สำเร็จ")
                st.rerun()

        st.markdown("---")
        st.markdown("**รายการหมวดหมู่ปัจจุบัน:**")
        for idx, cat_item in enumerate(st.session_state.categories_list):
            cols_c = st.columns([3, 1.5])
            cols_c[0].write(f"{idx + 1}. {cat_item}")
            action_c = cols_c[1].selectbox("จัดการ", ["เลือก", "แก้ไข", "ลบ"], key=f"action_cat_{idx}", label_visibility="collapsed")
            
            if action_c == "ลบ":
                st.session_state.categories_list.pop(idx)
                st.success(f"ลบหมวดหมู่ '{cat_item}' เรียบร้อยแล้ว")
                st.rerun()
            elif action_c == "แก้ไข":
                st.session_state[f"edit_mode_cat_{idx}"] = True

            if st.session_state.get(f"edit_mode_cat_{idx}", False):
                with st.form(f"form_edit_cat_{idx}"):
                    edited_c = st.text_input("แก้ไขชื่อหมวดหมู่", value=cat_item)
                    c_sc1, c_sc2 = st.columns(2)
                    if c_sc1.form_submit_button("บันทึก"):
                        st.session_state.categories_list[idx] = edited_c
                        st.session_state[f"edit_mode_cat_{idx}"] = False
                        st.success("แก้ไขสำเร็จ")
                        st.rerun()
                    if c_sc2.form_submit_button("ยกเลิก"):
                        st.session_state[f"edit_mode_cat_{idx}"] = False
                        st.rerun()

    with tab_manage_supplier:
        st.subheader("จัดการ/เพิ่มบริษัทที่จัดซื้อสินค้า (Supplier Profile)")
        
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
        st.markdown("**รายการบริษัทที่จัดซื้อปัจจุบัน:**")
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
                        if c_ss1.form_submit_button("บันทึกการแก้ไข"):
                            st.session_state.suppliers_list[idx] = {
                                "name": ed_name,
                                "address": ed_addr,
                                "tax_id": ed_tax,
                                "contact": ed_cont
                            }
                            st.session_state[f"edit_mode_sup_{idx}"] = False
                            st.success("แก้ไขข้อมูลสำเร็จ")
                            st.rerun()
                        if c_ss2.form_submit_button("ยกเลิก"):
                            st.session_state[f"edit_mode_sup_{idx}"] = False
                            st.rerun()
                st.markdown("---")
