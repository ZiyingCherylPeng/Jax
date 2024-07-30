import streamlit as st
import os
import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_tags(folder_path):
    items = os.listdir(folder_path)
    image_files = [item for item in items if item.endswith('.jpg')]
    
    image_tags = ""
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        encoded_image = image_to_base64(image_path)
        image_tags += f'<div class="scroll-item"><img src="data:image/jpeg;base64,{encoded_image}" alt="{image_file}"></div>'
        
    return image_tags

folder_path = 'C:/Users/zp111454/Desktop/Jax/images'  
image_tags = get_image_tags(folder_path)

# st.image("C:/Users/zp111454/Desktop/Jax/images/Jax_photo.jpg")

st.markdown(f"""
                <div class="scrollviewer">
                    <div class="scroll-content">
                        {image_tags}
                    </div>
                </div>
            """, unsafe_allow_html=True)
# st.markdown("""
#             <div id="popup" class="popup">
#                 <span class="close">&times;</span>
#                 <img class="popup-content" id="popup-img">
#             </div>
#             <script src="https://code.jquery.com/jquery-3.6.1.js"></script>
#             <script type="text/javascript">
#                 // Get the popup
#                 var popup = document.getElementById("popup");

#                 // Get the image and insert it inside the popup
#                 var popupImg = document.getElementById("popup-img");
#                 var images = document.querySelectorAll(".scroll-item img");
#                 images.forEach(image => {
#                     image.onclick = function(){
#                         popup.style.display = "block";
#                         popupImg.src = this.src;
#                     }
#                 });

#                 // Get the <span> element that closes the popup
#                 var span = document.getElementsByClassName("close")[0];

#                 // When the user clicks on <span> (x), close the popup
#                 span.onclick = function() {
#                     popup.style.display = "none";
#                 }

#                 // When the user clicks anywhere outside of the popup image, close it
#                 popup.onclick = function(event) {
#                     if (event.target == popup) {
#                         popup.style.display = "none";
#                     }
#                 }

#             </script>
                        
#         """, unsafe_allow_html=True)


st.markdown("""
            <script>
            alert('Hello, Streamlit!');
            </script>
            """, unsafe_allow_html=True)
