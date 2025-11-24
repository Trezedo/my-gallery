const { createApp, ref, reactive, computed, onMounted, watch, nextTick } = Vue;

createApp({
  setup() {
    const data = ref(null);
    const loading = ref(true);
    const selectedFolder = ref(".");
    const baseUrl = "/img/";
    const showModal = ref(false);
    const currentLargeImage = ref("");

    // 加载图片数据
    const loadImages = async () => {
      try {
        loading.value = true;
        const response = await fetch("/static/images.json");
        if (!response.ok) {
          throw new Error("无法加载数据");
        }
        data.value = await response.json();
        loading.value = false;
      } catch (error) {
        console.error("加载数据失败:", error);
        data.value = null;
        loading.value = false;
      }
    };

    // 文件夹列表
    const folders = computed(() => {
      if (!data.value) return {};
      return data.value.images;
    });

    // 当前选中文件夹的图片列表
    const currentImages = computed(() => {
      if (!data.value || !selectedFolder.value) return [];
      return data.value.images[selectedFolder.value] || [];
    });

    // 选择文件夹
    const selectFolder = (folderName) => {
      selectedFolder.value = folderName;
    };

    // 获取图片路径
    const getImagePath = (imageName) => {
      if (selectedFolder.value === ".") {
        return baseUrl + imageName;
      } else {
        console.log(`${selectedFolder.value}/${imageName}`);
        return baseUrl + `${selectedFolder.value}/${imageName}`;
      }
    };

    // 格式化图片大小
    const formatImageSize = (size) => {
      if (!size) return "未知大小";
      if (size < 1024) {
        return size + " B";
      } else if (size < 1024 * 1024) {
        return (size / 1024).toFixed(1) + " KB";
      } else {
        return (size / (1024 * 1024)).toFixed(1) + " MB";
      }
    };

    // 查看大图
    const viewLargeImage = (imagePath) => {
      currentLargeImage.value = imagePath;
      showModal.value = true;
    };

    // 关闭模态框
    const closeModal = () => {
      showModal.value = false;
      currentLargeImage.value = "";
    };

    const notification = reactive({ value: false, message: "" });
    const showCopyNotification = (msg) => {
      notification.message = msg;
      notification.value = true;
      setTimeout(() => {
        notification.value = false;
      }, 2000);
    };

    // 复制图片链接,区分 URL 和 MarkDown 格式
    const copyImageLink = async (image, format = "url") => {
      let link = location.href.replace(/\/$/, "") + getImagePath(image.name);
      let copyText = link;
      if (format === "md") {
        copyText = `![${image.name}](${link})`;
      }
      try {
        await navigator.clipboard.writeText(copyText);
        showCopyNotification("图片链接已复制到剪贴板");
      } catch (err) {
        console.error("复制失败:", err);
        // 降级方案
        const textArea = document.createElement("textarea");
        textArea.value = copyText;
        document.body.appendChild(textArea);
        textArea.select();
        try {
          document.execCommand("copy");
          showCopyNotification("图片链接已复制到剪贴板");
        } catch (fallbackErr) {
          console.error("降级复制也失败了:", fallbackErr);
        }
        document.body.removeChild(textArea);
      }
    };

    // 图片加载完成
    const imageLoaded = (event) => {
      event.target.classList.remove("shimmer");
    };

    // 图片加载失败
    const imageError = (event) => {
      event.target.src =
        "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDIwMCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMTUwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik03NSA1MEgxMjVNODcuNSAzNy41VjYyLjUiIHN0cm9rZT0iIzlDQTBCMyIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPHBhdGggZD0iTTYwIDkwSDE0ME0xMDAgNzVWMTA1IiBzdHJva2U9IiM5Q0EwQjMiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=";
      event.target.alt = "图片加载失败";
      event.target.classList.remove("shimmer");
    };

    // 新增：整理相关状态
    const showOrganizeModal = ref(false);
    const organizeLoading = ref(false);
    const organizePreview = ref([]);
    const organizeMode = ref("byTime"); // 'byTime' 或 'rename'
    // 新增：预览整理
    const previewOrganize = async () => {
      try {
        organizeLoading.value = true;
        showOrganizeModal.value = true;

        // 请求后端计算整理预览
        const response = await fetch("/api/preview-organize", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            mode: organizeMode.value,
            folder: selectedFolder.value,
          }),
        });

        if (!response.ok) {
          throw new Error("预览请求失败");
        }

        const previewData = await response.json();
        organizePreview.value = previewData.preview || [];
      } catch (error) {
        console.error("整理预览失败:", error);
        showCopyNotification("整理预览失败: " + error.message);
      } finally {
        organizeLoading.value = false;
      }
    };

    // 新增：确认整理
    const confirmOrganize = async () => {
      try {
        organizeLoading.value = true;

        // 请求后端执行整理
        const response = await fetch("/api/confirm-organize", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            mode: organizeMode.value,
            folder: selectedFolder.value,
            preview: organizePreview.value,
          }),
        });

        if (!response.ok) {
          throw new Error("整理操作失败");
        }

        const result = await response.json();
        showCopyNotification("图片整理完成！");
        closeOrganizeModal();

        // 重新加载图片数据
        await loadImages();
      } catch (error) {
        console.error("整理操作失败:", error);
        showCopyNotification("整理操作失败: " + error.message);
      } finally {
        organizeLoading.value = false;
      }
    };

    // 新增：关闭整理模态框
    const closeOrganizeModal = () => {
      showOrganizeModal.value = false;
      organizePreview.value = [];
      organizeLoading.value = false;
    };

    onMounted(() => {
      loadImages();
    });

    return {
      data,
      loading,
      selectedFolder,
      folders,
      currentImages,
      showModal,
      currentLargeImage,
      notification,
      selectFolder,
      getImagePath,
      formatImageSize,
      viewLargeImage,
      closeModal,
      copyImageLink,
      imageLoaded,
      imageError,
      loadImages,

      showOrganizeModal,
      organizeLoading,
      organizePreview,
      organizeMode,
      previewOrganize,
      confirmOrganize,
      closeOrganizeModal,
    };
  },
}).mount("#app");
