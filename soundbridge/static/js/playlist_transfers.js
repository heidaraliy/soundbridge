
function toSlug(serviceName) {
    serviceName = serviceName.replace(/\.$/, '');

    return serviceName
        .toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^a-z0-9-]/g, '');
}

// toggle dropdown
function toggleDropdown(containerClass) {
    var options = document.querySelector('.' + containerClass + ' .custom-options');
    var caret = document.querySelector('.' + containerClass + ' .dropdown-caret');

    var isOptionsVisible = options.style.display === 'block';

    // toggle options
    options.style.display = isOptionsVisible ? 'none' : 'block';

    // toggle caret
    caret.textContent = isOptionsVisible ? 'arrow_drop_down' : 'arrow_drop_up';
}

// close on click outside
window.onclick = function(event) {
    if (!event.target.matches('.selected-value')) {
        var dropdowns = document.querySelectorAll('.custom-select');
        dropdowns.forEach(function(dropdown) {
            var options = dropdown.querySelector('.custom-options');
            if (options.style.display === 'block') {
                options.style.display = 'none';
                var caret = dropdown.querySelector('.dropdown-caret');
                caret.textContent = "arrow_drop_down";
            }
        });
    }
}

// user clicks an option -- need to set value
function selectOption(containerClass, serviceName, logoPath) {
    var selectedValueContainer = document.querySelector('.' + containerClass + ' .selected-value');
    serviceName = toSlug(serviceName)

    // clear container
    selectedValueContainer.innerHTML = '';

    // service logo
    var img = document.createElement('img');
    img.src = logoPath;
    img.alt = serviceName;
    img.className = 'service-logo';

    // service name
    var name = document.createElement('span');
    name.textContent = serviceName;

    // create caret
    var caret = document.createElement('span');
    caret.classList.add('material-symbols-outlined', 'dropdown-caret');
    caret.style.marginLeft = "auto";
    caret.textContent = "arrow_drop_down";
    
    // all together now!
    selectedValueContainer.appendChild(img);
    selectedValueContainer.appendChild(name);
    selectedValueContainer.appendChild(caret);

    // close dropdown
    toggleDropdown(containerClass);
    fetchPlaylistsForService(serviceName);

    // reapply styling
    name.textContent = serviceName + ".";
}

function fetchPlaylistsForService(serviceName) {
    fetch('/api/get-playlists/' + serviceName)
        .then(response => response.json())
        .then(data => {
            console.log('Playlists: ', data.playlists);
            renderPlaylists(data.playlists);
        })
        .catch(error => {
            console.error('Error fetching playlists: ', error);
        });
}

function renderPlaylists(playlists) {
    var playlistContainer = document.getElementById('playlistContainer');
    playlistContainer.innerHTML = '';

    playlists.forEach(function(playlistName) {
        var playlistElement = document.createElement('div');
        playlistElement.className = 'playlist-transfer-link';
        playlistElement.textContent = playlistName;

        playlistContainer.appendChild(playlistElement);
    });
}