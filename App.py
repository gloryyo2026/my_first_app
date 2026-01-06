import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime


class HyperMeshProcessManager:
    def __init__(self, root):
        self.root = root
        self.root.title("HyperMesh Standard Workflow UI (Process Manager)")
        self.root.geometry("1200x700")
        
        # 단계별 완료 상태 추적
        self.step_completed = {
            "Step 1": False,
            "Step 2": False,
            "Step 3": False,
            "Step 4": False,
            "Step 5": False
        }
        
        # 현재 파일 정보
        self.current_file = ""
        self.current_solver = ""
        
        self._create_main_layout()
        self._create_steps()
        self._update_step_access()
        
    def _create_main_layout(self):
        """메인 레이아웃 생성"""
        # 좌측: Notebook (단계별 탭)
        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.notebook = ttk.Notebook(left_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)
        
        # 우측: 로그 박스
        right_frame = ttk.Frame(self.root, width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        right_frame.pack_propagate(False)
        
        ttk.Label(right_frame, text="작업 로그", font=("Arial", 12, "bold")).pack(pady=5)
        
        log_frame = ttk.Frame(right_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                               font=("Consolas", 9), bg="#f5f5f5")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # 하단: 진행 상태 바
        status_frame = ttk.Frame(right_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(status_frame, text="전체 진행률:").pack()
        self.progress = ttk.Progressbar(status_frame, length=300, mode='determinate')
        self.progress.pack(pady=5)
        
    def _create_steps(self):
        """각 단계별 탭 생성"""
        self.step1_frame = self._create_step1()
        self.step2_frame = self._create_step2()
        self.step3_frame = self._create_step3()
        self.step4_frame = self._create_step4()
        self.step5_frame = self._create_step5()
        
        self.notebook.add(self.step1_frame, text="Step 1: Setup")
        self.notebook.add(self.step2_frame, text="Step 2: Cleanup")
        self.notebook.add(self.step3_frame, text="Step 3: Meshing")
        self.notebook.add(self.step4_frame, text="Step 4: Property")
        self.notebook.add(self.step5_frame, text="Step 5: Boundary")
        
    def _create_step1(self):
        """Step 1: Setup 탭"""
        frame = ttk.Frame(self.notebook)
        
        ttk.Label(frame, text="Step 1: 모델 준비", font=("Arial", 14, "bold")).pack(pady=10)
        
        # 파일 불러오기
        file_frame = ttk.LabelFrame(frame, text="파일 불러오기", padding=10)
        file_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(file_frame, text="CAD/HM 파일 불러오기", 
                  command=self._import_file).pack(pady=5)
        
        ttk.Label(file_frame, text="현재 파일:").pack(anchor=tk.W, pady=(10,0))
        self.txt_file_path = ttk.Entry(file_frame, state="readonly", width=50)
        self.txt_file_path.pack(fill=tk.X, pady=5)
        
        # Solver 선택
        solver_frame = ttk.LabelFrame(frame, text="Solver 설정", padding=10)
        solver_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(solver_frame, text="Solver:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cmb_solver = ttk.Combobox(solver_frame, values=["OptiStruct", "Abaqus", "Nastran", "LS-DYNA"],
                                       state="readonly", width=30)
        self.cmb_solver.grid(row=0, column=1, padx=10, pady=5)
        self.cmb_solver.current(0)
        
        ttk.Label(solver_frame, text="단위계:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.cmb_unit = ttk.Combobox(solver_frame, values=["mm-ton-s", "m-kg-s", "inch-lb-s"],
                                     state="readonly", width=30)
        self.cmb_unit.grid(row=1, column=1, padx=10, pady=5)
        self.cmb_unit.current(0)
        
        # 완료 버튼
        ttk.Button(frame, text="Step 1 완료", command=self._complete_step1,
                  style="Accent.TButton").pack(pady=20)
        
        return frame
        
    def _create_step2(self):
        """Step 2: Cleanup 탭"""
        frame = ttk.Frame(self.notebook)
        
        ttk.Label(frame, text="Step 2: 기하 정리", font=("Arial", 14, "bold")).pack(pady=10)
        
        # 검사 영역
        check_frame = ttk.LabelFrame(frame, text="기하 검사", padding=10)
        check_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(check_frame, text="Free Edge 및 중복 서피스 검사",
                  command=self._check_geometry).pack(fill=tk.X, pady=5)
        
        # 자동 정리
        auto_frame = ttk.LabelFrame(frame, text="자동 정리", padding=10)
        auto_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(auto_frame, text="톨러런스:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ent_tolerance = ttk.Entry(auto_frame, width=15)
        self.ent_tolerance.insert(0, "0.1")
        self.ent_tolerance.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Button(auto_frame, text="자동 봉합 실행",
                  command=self._auto_cleanup).grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Label(auto_frame, text="필렛/홀 제거 R값:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.ent_r_value = ttk.Entry(auto_frame, width=15)
        self.ent_r_value.insert(0, "2.0")
        self.ent_r_value.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Button(auto_frame, text="Defeature 실행",
                  command=self._auto_defeature).grid(row=3, column=0, columnspan=2, pady=10)
        
        # 수동 편집
        ttk.Button(frame, text="수동 편집 툴 활성화",
                  command=self._manual_edit).pack(pady=10)
        
        ttk.Button(frame, text="Step 2 완료", command=self._complete_step2,
                  style="Accent.TButton").pack(pady=20)
        
        return frame
        
    def _create_step3(self):
        """Step 3: Meshing 탭"""
        frame = ttk.Frame(self.notebook)
        
        ttk.Label(frame, text="Step 3: 격자 생성", font=("Arial", 14, "bold")).pack(pady=10)
        
        # 메싱 설정
        mesh_frame = ttk.LabelFrame(frame, text="메싱 설정", padding=10)
        mesh_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(mesh_frame, text="Target Element Size:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ent_mesh_size = ttk.Entry(mesh_frame, width=15)
        self.ent_mesh_size.insert(0, "5.0")
        self.ent_mesh_size.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(mesh_frame, text="요소 타입:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.cmb_elem_type = ttk.Combobox(mesh_frame, values=["Quad", "Tria", "Mixed"],
                                         state="readonly", width=20)
        self.cmb_elem_type.grid(row=1, column=1, padx=10, pady=5)
        self.cmb_elem_type.current(0)
        
        ttk.Button(mesh_frame, text="메싱 실행",
                  command=self._run_mesh).grid(row=2, column=0, columnspan=2, pady=10)
        
        # 품질 검사
        quality_frame = ttk.LabelFrame(frame, text="품질 검사", padding=10)
        quality_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(quality_frame, text="품질 검사 실행",
                  command=self._quality_check).pack(pady=5)
        
        ttk.Button(frame, text="Step 3 완료", command=self._complete_step3,
                  style="Accent.TButton").pack(pady=20)
        
        return frame
        
    def _create_step4(self):
        """Step 4: Property 탭"""
        frame = ttk.Frame(self.notebook)
        
        ttk.Label(frame, text="Step 4: 속성 정의", font=("Arial", 14, "bold")).pack(pady=10)
        
        # 재질 설정
        mat_frame = ttk.LabelFrame(frame, text="재질 라이브러리", padding=10)
        mat_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(mat_frame, text="표준 재질:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cmb_mat_lib = ttk.Combobox(mat_frame, 
                                       values=["Steel (SPHC)", "Aluminum (AL6061)", "Carbon Steel (SS400)"],
                                       state="readonly", width=30)
        self.cmb_mat_lib.grid(row=0, column=1, padx=10, pady=5)
        self.cmb_mat_lib.current(0)
        
        ttk.Button(mat_frame, text="재질 적용",
                  command=self._apply_material).grid(row=1, column=0, columnspan=2, pady=10)
        
        # 두께 설정
        thick_frame = ttk.LabelFrame(frame, text="두께 설정", padding=10)
        thick_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(thick_frame, text="메타데이터 기반 두께 자동 매칭",
                  command=self._map_thickness).pack(pady=5)
        
        ttk.Button(thick_frame, text="3D 두께 시각화",
                  command=self._visualize_thickness).pack(pady=5)
        
        ttk.Button(frame, text="Step 4 완료", command=self._complete_step4,
                  style="Accent.TButton").pack(pady=20)
        
        return frame
        
    def _create_step5(self):
        """Step 5: Boundary Conditions 탭"""
        frame = ttk.Frame(self.notebook)
        
        ttk.Label(frame, text="Step 5: 경계 조건", font=("Arial", 14, "bold")).pack(pady=10)
        
        # 구속 조건
        spc_frame = ttk.LabelFrame(frame, text="구속 조건 (SPC)", padding=10)
        spc_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(spc_frame, text="자유도 제어:").pack(anchor=tk.W, pady=5)
        
        dof_frame = ttk.Frame(spc_frame)
        dof_frame.pack(fill=tk.X, pady=5)
        
        self.dof_vars = []
        for i in range(1, 7):
            var = tk.BooleanVar()
            ttk.Checkbutton(dof_frame, text=f"DOF {i}", variable=var).pack(side=tk.LEFT, padx=5)
            self.dof_vars.append(var)
        
        preset_frame = ttk.Frame(spc_frame)
        preset_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(preset_frame, text="Full Fix", command=self._set_full_fix).pack(side=tk.LEFT, padx=5)
        ttk.Button(preset_frame, text="Pinned", command=self._set_pinned).pack(side=tk.LEFT, padx=5)
        
        # 하중 조건
        load_frame = ttk.LabelFrame(frame, text="하중 조건", padding=10)
        load_frame.pack(fill=tk.X, padx=20, pady=10)
        
        force_input_frame = ttk.Frame(load_frame)
        force_input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(force_input_frame, text="하중 크기:").pack(side=tk.LEFT, padx=5)
        self.ent_force_val = ttk.Entry(force_input_frame, width=15)
        self.ent_force_val.insert(0, "1000")
        self.ent_force_val.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(force_input_frame, text="N").pack(side=tk.LEFT)
        
        # 최종 완료
        final_frame = ttk.Frame(frame)
        final_frame.pack(pady=20)
        
        ttk.Button(final_frame, text="Load Case 생성",
                  command=self._finalize_step).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(final_frame, text="Solver Deck 내보내기",
                  command=self._export_deck).pack(side=tk.LEFT, padx=5)
        
        return frame
        
    def _log(self, message, level="INFO"):
        """로그 출력"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 레벨별 색상
        if level == "ERROR":
            start = self.log_text.index("end-2l")
            end = self.log_text.index("end-1l")
            self.log_text.tag_add("error", start, end)
            self.log_text.tag_config("error", foreground="red")
        elif level == "SUCCESS":
            start = self.log_text.index("end-2l")
            end = self.log_text.index("end-1l")
            self.log_text.tag_add("success", start, end)
            self.log_text.tag_config("success", foreground="green")
            
    def _update_progress(self):
        """진행률 업데이트"""
        completed = sum(1 for v in self.step_completed.values() if v)
        progress_percent = (completed / 5) * 100
        self.progress['value'] = progress_percent
        
    def _update_step_access(self):
        """단계별 접근 제어"""
        for i in range(5):
            if i == 0:
                continue
            step_name = f"Step {i+1}"
            prev_step = f"Step {i}"
            
            if not self.step_completed[prev_step]:
                self.notebook.tab(i, state="disabled")
            else:
                self.notebook.tab(i, state="normal")
                
    def _on_tab_change(self, event):
        """탭 변경 시 이벤트"""
        current_tab = self.notebook.index(self.notebook.select())
        
        # 이전 단계로 돌아갈 때 경고
        if current_tab > 0:
            prev_step = f"Step {current_tab}"
            if self.step_completed[prev_step]:
                response = messagebox.askyesno(
                    "경고",
                    f"{prev_step}이 이미 완료되었습니다.\n이전 단계로 돌아가면 해당 단계부터 다시 수행해야 합니다.\n계속하시겠습니까?"
                )
                if response:
                    # 현재 및 이후 단계 미완료 처리
                    for i in range(current_tab, 6):
                        if i <= 5:
                            step = f"Step {i}"
                            self.step_completed[step] = False
                    self._update_progress()
                    self._log(f"{prev_step}으로 회귀. 이후 단계 재수행 필요", "WARNING")
                    
    # Step 1 기능들
    def _import_file(self):
        file_path = filedialog.askopenfilename(
            title="CAD/HM 파일 선택",
            filetypes=[("All Supported", "*.hm *.catpart *.stp *.igs"),
                      ("HyperMesh", "*.hm"),
                      ("CATIA", "*.catpart"),
                      ("STEP", "*.stp"),
                      ("IGES", "*.igs")]
        )
        
        if file_path:
            self.current_file = file_path
            self.txt_file_path.config(state="normal")
            self.txt_file_path.delete(0, tk.END)
            self.txt_file_path.insert(0, file_path)
            self.txt_file_path.config(state="readonly")
            
            # 단위계 변환 확인
            response = messagebox.askyesno(
                "단위계 변환",
                f"선택한 파일: {file_path}\n\n단위계 변환(Scaling)이 필요합니까?"
            )
            
            if response:
                self._log(f"파일 로드 완료: {file_path} (단위계 변환 적용)", "SUCCESS")
            else:
                self._log(f"파일 로드 완료: {file_path}", "SUCCESS")
                
    def _complete_step1(self):
        if not self.current_file:
            messagebox.showerror("오류", "파일을 먼저 불러와주세요.")
            return
            
        self.current_solver = self.cmb_solver.get()
        self.step_completed["Step 1"] = True
        self._update_progress()
        self._update_step_access()
        self._log(f"Step 1 완료 - Solver: {self.current_solver}, 단위계: {self.cmb_unit.get()}", "SUCCESS")
        messagebox.showinfo("완료", "Step 1이 완료되었습니다. Step 2로 진행합니다.")
        self.notebook.select(1)  # Step 2로 이동
        
    # Step 2 기능들
    def _check_geometry(self):
        self._log("기하 검사 시작...", "INFO")
        # 시뮬레이션
        self.root.after(1000, lambda: self._log("Free Edge 3개 발견", "WARNING"))
        self.root.after(1500, lambda: self._log("중복 서피스 1개 발견", "WARNING"))
        
    def _auto_cleanup(self):
        tolerance = self.ent_tolerance.get()
        self._log(f"자동 봉합 시작 (톨러런스: {tolerance})", "INFO")
        self.root.after(2000, lambda: self._log("봉합 완료: 3개 에지 처리됨", "SUCCESS"))
        
    def _auto_defeature(self):
        r_value = self.ent_r_value.get()
        self._log(f"Defeature 실행 (R < {r_value})", "INFO")
        self.root.after(2000, lambda: self._log("5개 피처 제거 완료", "SUCCESS"))
        
    def _manual_edit(self):
        self._log("수동 편집 툴 활성화", "INFO")
        messagebox.showinfo("수동 편집", "HyperMesh 편집 툴이 활성화되었습니다.")
        
    def _complete_step2(self):
        self.step_completed["Step 2"] = True
        self._update_progress()
        self._update_step_access()
        self._log("Step 2 완료 - 기하 정리 완료", "SUCCESS")
        messagebox.showinfo("완료", "Step 2가 완료되었습니다. Step 3로 진행합니다.")
        self.notebook.select(2)  # Step 3으로 이동
        
    # Step 3 기능들
    def _run_mesh(self):
        mesh_size = self.ent_mesh_size.get()
        elem_type = self.cmb_elem_type.get()
        self._log(f"메싱 시작 (Size: {mesh_size}, Type: {elem_type})", "INFO")
        self.root.after(3000, lambda: self._log("메싱 완료: 15,234 요소 생성", "SUCCESS"))
        
    def _quality_check(self):
        self._log("품질 검사 시작...", "INFO")
        self.root.after(2000, lambda: self._log("Jacobian: 최소 0.78, 평균 0.95", "INFO"))
        self.root.after(2500, lambda: self._log("Aspect Ratio: 최대 3.2, 평균 1.8", "INFO"))
        self.root.after(3000, lambda: self._log("품질 기준 만족", "SUCCESS"))
        
    def _complete_step3(self):
        self.step_completed["Step 3"] = True
        self._update_progress()
        self._update_step_access()
        self._log("Step 3 완료 - 메싱 완료", "SUCCESS")
        messagebox.showinfo("완료", "Step 3이 완료되었습니다. Step 4로 진행합니다.")
        self.notebook.select(3)  # Step 4로 이동
        
    # Step 4 기능들
    def _apply_material(self):
        material = self.cmb_mat_lib.get()
        self._log(f"재질 적용: {material}", "SUCCESS")
        
    def _map_thickness(self):
        self._log("두께 자동 매칭 시작...", "INFO")
        self.root.after(1500, lambda: self._log("12개 컴포넌트 두께 매칭 완료", "SUCCESS"))
        
    def _visualize_thickness(self):
        self._log("3D 두께 시각화 활성화", "INFO")
        messagebox.showinfo("시각화", "Shell 두께가 3D로 표시됩니다.")
        
    def _complete_step4(self):
        self.step_completed["Step 4"] = True
        self._update_progress()
        self._update_step_access()
        self._log("Step 4 완료 - 속성 정의 완료", "SUCCESS")
        messagebox.showinfo("완료", "Step 4가 완료되었습니다. Step 5로 진행합니다.")
        self.notebook.select(4)  # Step 5로 이동
        
    # Step 5 기능들
    def _set_full_fix(self):
        for var in self.dof_vars:
            var.set(True)
        self._log("Full Fix 프리셋 적용 (모든 DOF 구속)", "INFO")
        
    def _set_pinned(self):
        for i, var in enumerate(self.dof_vars):
            var.set(i < 3)  # DOF 1-3만 체크
        self._log("Pinned 프리셋 적용 (DOF 1-3 구속)", "INFO")
        
    def _finalize_step(self):
        # 구속 확인
        has_constraint = any(var.get() for var in self.dof_vars)
        has_force = bool(self.ent_force_val.get())
        
        if has_force and not has_constraint:
            messagebox.showwarning("경고", "하중은 있으나 구속 조건이 없습니다!\n모델이 자유롭게 움직일 수 있습니다.")
            return
            
        self._log("Load Case 생성 완료", "SUCCESS")
        messagebox.showinfo("완료", "Load Case가 생성되었습니다.")
        
    def _export_deck(self):
        file_path = filedialog.asksaveasfilename(
            title="Solver Deck 내보내기",
            defaultextension=".fem",
            filetypes=[("FEM", "*.fem"), ("INP", "*.inp"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.step_completed["Step 5"] = True
            self._update_progress()
            self._log(f"Solver Deck 내보내기 완료: {file_path}", "SUCCESS")
            messagebox.showinfo("완료", "전체 작업이 완료되었습니다!")


if __name__ == "__main__":
    root = tk.Tk()
    app = HyperMeshProcessManager(root)
    root.mainloop()
