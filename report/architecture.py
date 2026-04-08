"""
Architecture diagram generator for the Smart Campus Lost & Found System.
Produces a PNG using matplotlib that illustrates the three-tier architecture
and AWS service integration.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def draw_box(ax, x, y, w, h, label, color="#dbeafe", edge="#2563eb", fontsize=9):
    """Draw a rounded rectangle with a centred label."""
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02",
        facecolor=color,
        edgecolor=edge,
        linewidth=1.5,
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, label,
            ha="center", va="center", fontsize=fontsize, fontweight="bold")


def draw_arrow(ax, x1, y1, x2, y2):
    """Draw a simple arrow between two points."""
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color="#64748b", lw=1.5))


def generate_diagram(output_path="architecture.png"):
    """Generate and save the architecture diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.set_title("Smart Campus Lost & Found System -- Architecture",
                 fontsize=14, fontweight="bold", pad=20)

    # -- Presentation Tier --
    draw_box(ax, 0.5, 7.0, 4.0, 1.5, "React Frontend\n(Port 3001)", "#dbeafe", "#2563eb")
    ax.text(2.5, 8.7, "Presentation Tier", ha="center", fontsize=10, fontstyle="italic", color="#64748b")

    # -- Application Tier --
    draw_box(ax, 5.5, 7.0, 4.0, 1.5, "Flask REST API\n(Port 5001)", "#d1fae5", "#16a34a")
    ax.text(7.5, 8.7, "Application Tier", ha="center", fontsize=10, fontstyle="italic", color="#64748b")

    # Custom library
    draw_box(ax, 5.5, 5.0, 4.0, 1.3, "campusfinder Library\n(ItemMatcher, LocationTracker,\nClaimProcessor, NotificationManager,\nAnalytics)", "#fef3c7", "#d97706", fontsize=7)

    # -- Data / Cloud Tier --
    ax.text(11.5, 8.7, "Cloud Services (AWS)", ha="center", fontsize=10, fontstyle="italic", color="#64748b")
    services = [
        ("Amazon DynamoDB", "#dbeafe"),
        ("Amazon S3", "#d1fae5"),
        ("Amazon Rekognition", "#fce7f3"),
        ("Amazon SNS", "#fef3c7"),
        ("Amazon CloudWatch", "#e0e7ff"),
        ("AWS Lambda", "#fae8ff"),
    ]
    for i, (name, color) in enumerate(services):
        ypos = 7.5 - i * 1.15
        draw_box(ax, 10.5, ypos, 3.0, 0.9, name, color, "#475569", fontsize=8)

    # Local DB
    draw_box(ax, 5.5, 3.2, 4.0, 1.0, "SQLite (Local Dev)\n/ DynamoDB (Prod)", "#e2e8f0", "#475569", fontsize=8)

    # -- Arrows --
    draw_arrow(ax, 4.5, 7.75, 5.5, 7.75)   # Frontend -> API
    draw_arrow(ax, 7.5, 7.0, 7.5, 6.3)      # API -> Library
    draw_arrow(ax, 7.5, 5.0, 7.5, 4.2)      # Library -> DB
    draw_arrow(ax, 9.5, 7.5, 10.5, 7.9)     # API -> DynamoDB
    draw_arrow(ax, 9.5, 7.3, 10.5, 6.8)     # API -> S3
    draw_arrow(ax, 9.5, 7.1, 10.5, 5.6)     # API -> Rekognition
    draw_arrow(ax, 9.5, 6.9, 10.5, 4.5)     # API -> SNS
    draw_arrow(ax, 9.5, 6.7, 10.5, 3.4)     # API -> CloudWatch
    draw_arrow(ax, 9.5, 6.5, 10.5, 2.2)     # API -> Lambda

    # Labels on arrows
    ax.text(5.0, 8.0, "REST API\n(JSON)", ha="center", fontsize=7, color="#64748b")

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Architecture diagram saved to {output_path}")


if __name__ == "__main__":
    generate_diagram()
