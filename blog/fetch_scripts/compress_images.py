"""
图片压缩脚本 - 将博客图片从 51MB 压缩到 10MB 以内
保留原始格式，不转换为 WebP
"""
import os
import shutil
from PIL import Image, UnidentifiedImageError
from pathlib import Path


def get_file_size_mb(path):
    """获取文件大小（MB）"""
    return os.path.getsize(path) / (1024 * 1024)


def compress_image(input_path, output_path, target_mb, min_quality=30, max_width=2000):
    """
    智能压缩图片：调整尺寸 + 质量
    保留原始格式
    """
    try:
        ext = Path(input_path).suffix.lower()
        is_png = ext == '.png'

        current_size = get_file_size_mb(input_path)
        if current_size <= target_mb:
            print(f"  已经足够小 ({current_size:.2f}MB <= {target_mb:.2f}MB)，跳过")
            return True

        with Image.open(input_path) as img:
            original_size = img.size

            # 转换 RGBA 为 RGB（JPEG 不支持 RGBA）
            if img.mode == 'RGBA' and not is_png:
                img = img.convert('RGB')
            elif img.mode == 'RGBA' and is_png:
                # PNG 保留 RGBA
                pass
            elif img.mode in ('CMYK', 'LA', 'P'):
                img = img.convert('RGB')

            # 第一步：缩小尺寸
            width, height = img.size
            if width > max_width:
                ratio = max_width / width
                new_size = (max_width, int(height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"  尺寸调整: {original_size} -> {new_size}")

            # 第二步：迭代降低质量
            if is_png:
                # PNG：先缩小尺寸，再减少颜色
                for colors in [256, 128, 64]:
                    if img.mode == 'RGBA':
                        quantized = img.quantize(colors=colors, method=Image.Quantize.FASTOCTREE)
                    else:
                        quantized = img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
                    quantized.save(output_path, 'PNG', optimize=True)
                    size = get_file_size_mb(output_path)
                    print(f"  colors={colors}, 大小={size:.2f}MB")
                    if size <= target_mb:
                        return True
            else:
                # JPEG：降低质量
                quality = 80
                while quality >= min_quality:
                    img.save(output_path, 'JPEG', quality=quality, optimize=True)
                    size = get_file_size_mb(output_path)
                    print(f"  quality={quality}, 大小={size:.2f}MB")
                    if size <= target_mb:
                        return True
                    quality -= 10

                # 最终保存
                img.save(output_path, 'JPEG', quality=min_quality, optimize=True)

        return True
    except UnidentifiedImageError:
        print(f"  无法识别图片格式: {input_path}")
        return False
    except OSError as e:
        print(f"  文件操作失败 {input_path}: {e}")
        return False
    except Exception as e:
        print(f"  压缩失败 {input_path}: {e}")
        return False


def main():
    images_dir = Path(__file__).parent.parent / "source" / "images"
    backup_dir = images_dir / "backup"

    backup_dir.mkdir(exist_ok=True)

    TARGET_TOTAL_MB = 10.0

    # 获取所有图片文件
    image_files = []
    for f in images_dir.iterdir():
        if f.is_file() and f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.gif'):
            image_files.append(f)

    image_files.sort(key=lambda f: f.stat().st_size, reverse=True)

    print(f"找到 {len(image_files)} 个图片文件")
    print(f"当前总大小: {sum(get_file_size_mb(f) for f in image_files):.2f}MB")
    print(f"目标总大小: {TARGET_TOTAL_MB}MB")
    print()

    # 分类
    small_files = [f for f in image_files if f.stat().st_size < 500 * 1024]
    large_files = [f for f in image_files if f.stat().st_size >= 500 * 1024]

    small_total = sum(get_file_size_mb(f) for f in small_files)
    target_for_large = TARGET_TOTAL_MB - small_total

    print(f"小文件 ({len(small_files)}个): {small_total:.2f}MB (保持原样)")
    print(f"大文件 ({len(large_files)}个): 需压缩到 {target_for_large:.2f}MB")
    print()

    # 分配目标
    large_total = sum(get_file_size_mb(f) for f in large_files)
    targets = {}
    for f in large_files:
        size = get_file_size_mb(f)
        target = (size / large_total) * target_for_large
        target = max(target, 0.3)
        targets[f] = target

    # 处理所有图片
    for f in image_files:
        filename = f.name
        backup_path = backup_dir / filename

        print(f"处理: {filename} ({get_file_size_mb(f):.2f}MB)")

        # 备份
        if not backup_path.exists():
            shutil.copy2(f, backup_path)
            print(f"  备份到: backup/{filename}")

        if f in large_files:
            target = targets[f]
            print(f"  目标大小: {target:.2f}MB")
            compress_image(f, f, target)
        else:
            print(f"  小文件，保持原样")

    # 验证
    print("\n" + "="*50)
    print("压缩完成！验证结果：")
    print("="*50)

    final_total = 0
    for f in image_files:
        size = get_file_size_mb(f)
        final_total += size
        print(f"  {f.name}: {size:.2f}MB")

    print(f"\n最终总大小: {final_total:.2f}MB")
    print(f"目标: {TARGET_TOTAL_MB}MB")
    print(f"结果: {'达标' if final_total <= TARGET_TOTAL_MB else '未达标'}")
    print(f"\n压缩前: 51.00MB")
    print(f"压缩后: {final_total:.2f}MB")
    print(f"压缩率: {(1 - final_total/51)*100:.1f}%")


if __name__ == "__main__":
    main()
