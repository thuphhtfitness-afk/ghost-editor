#!/bin/bash
# HPF talking head: fonts with Vietnamese glyphs (Google Fonts, OFL) -> ~/.fonts, Fluent 3D emoji (MIT) -> ./emoji
set -e
mkdir -p ~/.fonts emoji
b=https://raw.githubusercontent.com/google/fonts/main/ofl
for u in "playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf" "oswald/Oswald%5Bwght%5D.ttf" "patrickhand/PatrickHand-Regular.ttf" \
         "bevietnampro/BeVietnamPro-SemiBold.ttf" "bevietnampro/BeVietnamPro-ExtraBold.ttf"; do
  curl -sS -fL -o ~/.fonts/$(basename "$u") "$b/$u"; done
fc-cache -f >/dev/null || true
e=https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets
get(){ curl -sS -fL -o "emoji/$1.png" "$e/$2/3D/$3"; }
get coffee "Hot%20beverage" hot_beverage_3d.png;      get bubbletea "Bubble%20tea" bubble_tea_3d.png
get fries "French%20fries" french_fries_3d.png;       get cookie "Cookie" cookie_3d.png
get bento "Bento%20box" bento_box_3d.png;             get sweat "Anxious%20face%20with%20sweat" anxious_face_with_sweat_3d.png
get weary "Weary%20face" weary_face_3d.png;           get zany "Zany%20face" zany_face_3d.png
get plate "Fork%20and%20knife%20with%20plate" fork_and_knife_with_plate_3d.png
get sparkles "Sparkles" sparkles_3d.png;              get star "Glowing%20star" glowing_star_3d.png
get hourglass "Hourglass%20not%20done" hourglass_not_done_3d.png
get yum "Face%20savoring%20food" face_savoring_food_3d.png; get down "Chart%20decreasing" chart_decreasing_3d.png
echo ok
