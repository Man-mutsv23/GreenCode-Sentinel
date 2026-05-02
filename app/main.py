"""
GreenCode Sentinel - Main Application
Flet-based dashboard for code sustainability analysis.
"""

import sys
import os
from pathlib import Path
from typing import cast, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import flet as ft
from ai_engine import CodeAnalyzer
from app.ui.styles import Colors, Typography, Spacing, BorderRadius, Shadows
from app.ui.styles import get_grade_color, get_score_color, create_card_style
from app.utils.security import check_rate_limit


class GreenCodeSentinelApp:
    """Main application class for GreenCode Sentinel."""
    
    def __init__(self, page: ft.Page):
        """Initialize the application."""
        self.page = page
        self.analyzer = None
        self.current_results = None
        self.selected_file_path = None
        
        # Configure page
        self.page.title = "GreenCode Sentinel - AI-Powered Carbon Footprint Analyzer"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.bgcolor = Colors.BACKGROUND
        self.page.window.width = 1200
        self.page.window.height = 800
        self.page.window.min_width = 800
        self.page.window.min_height = 600
        
        # Initialize FilePicker
        self.file_picker = ft.FilePicker()
        self.file_picker.on_result = self.on_file_picked  # type: ignore
        self.page.overlay.append(self.file_picker)
        
        # Initialize analyzer
        try:
            self.analyzer = CodeAnalyzer()
        except Exception as e:
            self.show_error(f"Failed to initialize analyzer: {e}")
        
        # Build UI
        self.build_ui()
    
    def build_ui(self):
        """Build the main user interface."""
        # Header
        header = self.create_header()
        
        # Main content area
        content = ft.Container(
            content=ft.Column(
                [
                    self.create_upload_section(),
                    ft.Divider(height=Spacing.LG, color=Colors.DIVIDER),
                    self.create_results_section(),
                ],
                spacing=Spacing.LG,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=Spacing.XL,
            expand=True,
        )
        
        # Add to page
        self.page.add(
            ft.Column(
                [header, content],
                spacing=0,
                expand=True,
            )
        )
    
    def create_header(self) -> ft.Container:
        """Create the application header."""
        text_column: ft.Control = ft.Column(
            [
                ft.Text(
                    "🌱 GreenCode Sentinel",
                    size=Typography.TITLE_SIZE,
                    weight=ft.FontWeight.BOLD,
                    color=Colors.SURFACE,
                ),
                ft.Text(
                    "AI-Powered Carbon Footprint Analyzer",
                    size=Typography.CAPTION_SIZE,
                    color=Colors.SURFACE,
                    opacity=0.9,
                ),
            ],
            spacing=0,
        )
        
        return ft.Container(
            content=text_column,
            bgcolor=Colors.PRIMARY,
            padding=Spacing.LG,
        )
    
    def create_upload_section(self) -> ft.Container:
        """Create the file upload section."""
        self.selected_file_text = ft.Text(
            "No file selected",
            size=Typography.BODY_SIZE,
            color=Colors.TEXT_SECONDARY,
        )
        
        self.analyze_button = ft.ElevatedButton(
            content=ft.Text("Analyze Code"),
            bgcolor=Colors.PRIMARY,
            color=Colors.SURFACE,
            on_click=self.analyze_code,
            disabled=True,
            elevation=Shadows.MD,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD),
            ),
        )
        
        upload_card = ft.Container(
            content=ft.Column(
                cast(List[ft.Control], [
                    ft.Text(
                        "Upload Source Code",
                        size=Typography.HEADING_SIZE,
                        weight=ft.FontWeight.BOLD,
                        color=Colors.TEXT_PRIMARY,
                    ),
                    ft.Text(
                        "Supported: Python (.py), Java (.java), JavaScript (.js)",
                        size=Typography.CAPTION_SIZE,
                        color=Colors.TEXT_SECONDARY,
                    ),
                    ft.Container(height=Spacing.MD),
                    ft.ElevatedButton(
                        content=ft.Text("Choose File"),
                        bgcolor=Colors.SECONDARY,
                        color=Colors.SURFACE,
                        on_click=lambda _: self.file_picker.pick_files(
                            allowed_extensions=["py", "java", "js", "jsx", "ts", "tsx"]
                        ),
                        elevation=Shadows.MD,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD),
                        ),
                    ),
                    ft.Container(height=Spacing.SM),
                    self.selected_file_text,
                    ft.Container(height=Spacing.MD),
                    self.analyze_button,
                ]),
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            **create_card_style(Shadows.MD),
        )
        
        return upload_card
    
    def create_results_section(self) -> ft.Container:
        """Create the results display section."""
        self.results_container = ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "ℹ️",
                                size=64,
                                color=Colors.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                "No analysis yet",
                                size=Typography.HEADING_SIZE,
                                color=Colors.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                "Upload a file and click 'Analyze Code' to get started",
                                size=Typography.BODY_SIZE,
                                color=Colors.TEXT_SECONDARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=Spacing.MD,
                    ),
                    padding=Spacing.XXL,
                )
            ],
            spacing=Spacing.LG,
        )
        
        return ft.Container(
            content=self.results_container,
            expand=True,
        )
    
    def on_file_picked(self, e):
        """Handle file selection with validation."""
        if e.files and len(e.files) > 0:
            file = e.files[0]
            
            # Validate file extension
            valid_extensions = ['.py', '.java', '.js', '.jsx', '.ts', '.tsx']
            file_ext = Path(file.path).suffix.lower()
            
            if file_ext not in valid_extensions:
                self.selected_file_text.value = f"Error: Unsupported file type '{file_ext}'"
                self.selected_file_text.color = Colors.ERROR
                self.analyze_button.disabled = True
                self.page.update()
                return
            
            # Validate file size (max 5MB)
            max_size = 5 * 1024 * 1024  # 5MB in bytes
            try:
                file_size = os.path.getsize(file.path)
                if file_size > max_size:
                    size_mb = file_size / (1024 * 1024)
                    self.selected_file_text.value = f"Error: File too large ({size_mb:.1f}MB). Max 5MB"
                    self.selected_file_text.color = Colors.ERROR
                    self.analyze_button.disabled = True
                    self.page.update()
                    return
            except OSError as e:
                self.selected_file_text.value = f"Error: Cannot read file"
                self.selected_file_text.color = Colors.ERROR
                self.analyze_button.disabled = True
                self.page.update()
                return
            
            # File is valid
            self.selected_file_path = file.path
            self.selected_file_text.value = f"Selected: {file.name}"
            self.selected_file_text.color = Colors.SUCCESS
            self.analyze_button.disabled = False
        else:
            self.selected_file_path = None
            self.selected_file_text.value = "No file selected"
            self.selected_file_text.color = Colors.TEXT_SECONDARY
            self.analyze_button.disabled = True
        
        self.page.update()
    
    def analyze_code(self, e):
        """Analyze the selected code file with rate limiting."""
        if not self.selected_file_path or not self.analyzer:
            self.show_error("Please select a file first")
            return
        
        # Check rate limit
        is_allowed, wait_time = check_rate_limit("code_analysis")
        if not is_allowed:
            self.show_error(
                f"Rate limit exceeded. Please wait {wait_time:.1f} seconds before analyzing again.\n"
                f"(Limit: 5 requests per minute)"
            )
            return
        
        # Show loading indicator
        self.show_loading()
        
        try:
            # Perform analysis
            results = self.analyzer.analyze_file(self.selected_file_path)
            self.current_results = results
            
            # Display results
            self.display_results(results)
            
        except Exception as e:
            self.show_error(f"Analysis failed: {str(e)}")
    
    def show_loading(self):
        """Show loading indicator."""
        self.results_container.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.ProgressRing(color=Colors.PRIMARY),
                        ft.Text(
                            "Analyzing code with Gemini 3 Pro...",
                            size=Typography.HEADING_SIZE,
                            color=Colors.TEXT_PRIMARY,
                        ),
                        ft.Text(
                            "Using high thinking level for deep analysis",
                            size=Typography.BODY_SIZE,
                            color=Colors.TEXT_SECONDARY,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=Spacing.MD,
                ),
                padding=Spacing.XXL,
            )
        ]
        self.page.update()
    
    def display_results(self, results: dict):
        """Display analysis results."""
        score = results.get('score', 0)
        grade = results.get('grade', 'F')
        
        # Score card
        score_card = self.create_score_card(score, grade, results)
        
        # Category breakdown
        category_card = self.create_category_card(results.get('category_scores', {}))
        
        # CO2 savings
        co2_card = self.create_co2_card(results)
        
        # Issues list
        issues_card = self.create_issues_card(results.get('issues', []))
        
        self.results_container.controls = [
            ft.Row(
                [score_card, category_card, co2_card],
                spacing=Spacing.LG,
                wrap=True,
            ),
            issues_card,
        ]
        
        self.page.update()
    
    def create_score_card(self, score: float, grade: str, results: dict) -> ft.Container:
        """Create the main score display card."""
        score_color = get_score_color(score)
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Sustainability Score",
                        size=Typography.HEADING_SIZE,
                        weight=ft.FontWeight.BOLD,
                        color=Colors.TEXT_PRIMARY,
                    ),
                    ft.Container(height=Spacing.MD),
                    ft.Text(
                        f"{score:.1f}",
                        size=64,
                        weight=ft.FontWeight.BOLD,
                        color=score_color,
                    ),
                    ft.Text(
                        f"Grade: {grade}",
                        size=Typography.SUBTITLE_SIZE,
                        weight=ft.FontWeight.BOLD,
                        color=score_color,
                    ),
                    ft.Container(height=Spacing.SM),
                    ft.Text(
                        f"Total Issues: {results.get('total_issues', 0)}",
                        size=Typography.BODY_SIZE,
                        color=Colors.TEXT_SECONDARY,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            **create_card_style(Shadows.LG),
            width=300,
        )
    
    def create_category_card(self, category_scores: dict) -> ft.Container:
        """Create category breakdown card."""
        categories = []
        for category, score in category_scores.items():
            categories.append(
                ft.Row(
                    [
                        ft.Text(
                            category.capitalize(),
                            size=Typography.BODY_SIZE,
                            color=Colors.TEXT_PRIMARY,
                            expand=True,
                        ),
                        ft.Text(
                            f"{score:.1f}",
                            size=Typography.BODY_SIZE,
                            weight=ft.FontWeight.BOLD,
                            color=get_score_color(score),
                        ),
                    ],
                    spacing=Spacing.MD,
                )
            )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Category Breakdown",
                        size=Typography.HEADING_SIZE,
                        weight=ft.FontWeight.BOLD,
                        color=Colors.TEXT_PRIMARY,
                    ),
                    ft.Container(height=Spacing.MD),
                    *categories,
                ],
            ),
            **create_card_style(Shadows.MD),
            width=300,
        )
    
    def create_co2_card(self, results: dict) -> ft.Container:
        """Create CO2 savings card."""
        co2_kg = results.get('co2_savings_kg_year', 0)
        co2_tons = results.get('co2_savings_tons_year', 0)
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "CO₂ Savings Potential",
                        size=Typography.HEADING_SIZE,
                        weight=ft.FontWeight.BOLD,
                        color=Colors.TEXT_PRIMARY,
                    ),
                    ft.Container(height=Spacing.MD),
                    ft.Text(
                        "☁️",
                        size=48,
                        color=Colors.SUCCESS,
                    ),
                    ft.Text(
                        f"{co2_kg:.2f} kg/year",
                        size=Typography.SUBTITLE_SIZE,
                        weight=ft.FontWeight.BOLD,
                        color=Colors.SUCCESS,
                    ),
                    ft.Text(
                        f"({co2_tons:.4f} tons/year)",
                        size=Typography.BODY_SIZE,
                        color=Colors.TEXT_SECONDARY,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            **create_card_style(Shadows.MD),
            width=300,
        )
    
    def create_issues_card(self, issues: list) -> ft.Container:
        """Create issues list card."""
        if not issues:
            return ft.Container(
                content=ft.Text(
                    "No issues found! Your code is optimized! 🎉",
                    size=Typography.HEADING_SIZE,
                    color=Colors.SUCCESS,
                    text_align=ft.TextAlign.CENTER,
                ),
                **create_card_style(Shadows.SM),
                padding=Spacing.XL,
            )
        
        issue_widgets = []
        for i, issue in enumerate(issues, 1):
            severity = issue.get('severity', 'Unknown')
            category = issue.get('category', 'Unknown')
            description = issue.get('description', 'No description')
            suggestion = issue.get('suggestion', 'No suggestion')
            
            # Severity color
            severity_colors = {
                'Critical': Colors.ERROR,
                'High': Colors.WARNING,
                'Medium': Colors.ACCENT,
                'Low': Colors.INFO,
            }
            severity_color = severity_colors.get(severity, Colors.TEXT_SECONDARY)
            
            issue_widgets.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text(
                                            severity,
                                            size=Typography.CAPTION_SIZE,
                                            color=Colors.SURFACE,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        bgcolor=severity_color,
                                        padding=ft.padding.symmetric(
                                            horizontal=Spacing.SM,
                                            vertical=Spacing.XS,
                                        ),
                                        border_radius=BorderRadius.SM,
                                    ),
                                    ft.Text(
                                        category.capitalize(),
                                        size=Typography.BODY_SIZE,
                                        color=Colors.TEXT_SECONDARY,
                                    ),
                                ],
                                spacing=Spacing.SM,
                            ),
                            ft.Text(
                                description,
                                size=Typography.BODY_SIZE,
                                color=Colors.TEXT_PRIMARY,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            "💡 Suggestion:",
                                            size=Typography.CAPTION_SIZE,
                                            weight=ft.FontWeight.BOLD,
                                            color=Colors.SUCCESS,
                                        ),
                                        ft.Text(
                                            suggestion,
                                            size=Typography.CAPTION_SIZE,
                                            color=Colors.TEXT_SECONDARY,
                                        ),
                                    ],
                                    spacing=Spacing.XS,
                                ),
                                bgcolor=Colors.SUCCESS + "1A",  # Add alpha for 10% opacity
                                padding=Spacing.SM,
                                border_radius=BorderRadius.SM,
                            ),
                        ],
                        spacing=Spacing.SM,
                    ),
                    **create_card_style(Shadows.SM),
                    margin=ft.margin.only(bottom=Spacing.MD),
                )
            )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        f"Issues Found ({len(issues)})",
                        size=Typography.HEADING_SIZE,
                        weight=ft.FontWeight.BOLD,
                        color=Colors.TEXT_PRIMARY,
                    ),
                    ft.Container(height=Spacing.SM),
                    ft.Column(
                        issue_widgets,
                        spacing=0,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
            ),
            **create_card_style(Shadows.MD),
        )
    
    def show_error(self, message: str):
        """Show error message."""
        self.results_container.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "⚠️",
                            size=64,
                            color=Colors.ERROR,
                        ),
                        ft.Text(
                            "Error",
                            size=Typography.HEADING_SIZE,
                            color=Colors.ERROR,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            message,
                            size=Typography.BODY_SIZE,
                            color=Colors.TEXT_PRIMARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=Spacing.MD,
                ),
                padding=Spacing.XXL,
            )
        ]
        self.page.update()


def main(page: ft.Page):
    """Main entry point for the Flet application."""
    GreenCodeSentinelApp(page)
ft.app(target=main)
