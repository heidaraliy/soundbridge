function toSlug(serviceName) {
    serviceName = serviceName.replace(/\.$/, '');

    return serviceName
        .toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^a-z0-9-]/g, '');
}

// toggle dropdown
function toggleDropdown(containerClass) {
    const options = document.querySelector(`.${containerClass} .custom-options`);
    const caret = document.querySelector(`.${containerClass} .dropdown-caret`);

    const isOptionsVisible = options.style.display === 'block';

    // toggle options
    options.style.display = isOptionsVisible ? 'none' : 'block';

    // toggle caret
    caret.textContent = isOptionsVisible ? 'arrow_drop_down' : 'arrow_drop_up';
}

// close on click outside, otherwise handle click
window.addEventListener('click', function (event) {
    if (!event.target.matches('.selected-value')) {
        const dropdowns = document.querySelectorAll('.custom-select');
        dropdowns.forEach(function (dropdown) {
            const options = dropdown.querySelector('.custom-options');
            if (options.style.display === 'block') {
                options.style.display = 'none';
                const caret = dropdown.querySelector('.dropdown-caret');
                caret.textContent = 'arrow_drop_down';
            }
        });
    }
});

// user clicks an option -- need to set value
function selectOption(containerClass, serviceName, logoPath) {
    const selectedValueContainer = document.querySelector(`.${containerClass} .selected-value`);
    serviceName = toSlug(serviceName);

    // clear container
    selectedValueContainer.innerHTML = '';

    // service logo
    const img = document.createElement('img');
    img.src = logoPath;
    img.alt = serviceName;
    img.className = 'service-logo';

    // service name
    const name = document.createElement('span');
    name.textContent = serviceName;

    // create caret
    const caret = document.createElement('span');
    caret.classList.add('material-symbols-outlined', 'dropdown-caret');
    caret.style.marginLeft = 'auto';
    caret.textContent = 'arrow_drop_down';

    // all together now!
    selectedValueContainer.appendChild(img);
    selectedValueContainer.appendChild(name);
    selectedValueContainer.appendChild(caret);

    // close dropdown and fetch playlists
    toggleDropdown(containerClass);
    if (containerClass === 'from-container') {
        fetchPlaylistsForService(serviceName);
    }

    // reapply styling
    name.textContent = `${serviceName}.`;
}

function fetchPlaylistsForService(serviceName) {
    fetch(`/api/get-playlists/${serviceName}`)
        .then(response => response.json())
        .then(data => {
            console.log('Playlists: ', data.playlists);
            renderPlaylists(data.playlists, 'from-container');
        })
        .catch(error => {
            console.error('Error fetching playlists: ', error);
        });
}

function renderPlaylists(playlists, containerClass) {
    const fromPlaylistContainer = document.querySelector(`.${containerClass} #playlistContainer`);
    fromPlaylistContainer.innerHTML = '';

    playlists.forEach(function (playlistName) {
        const playlistElement = document.createElement('div');
        playlistElement.id = toSlug(playlistName);
        playlistElement.className = 'playlist-transfer-link';
        playlistElement.textContent = playlistName;
        playlistElement.style.cursor = 'pointer';

        playlistElement.addEventListener('click', function () {
            transferPlaylist(playlistName, containerClass);
        });

        fromPlaylistContainer.appendChild(playlistElement);
    });
}

function getSelectedService(containerClass) {
    const selectedValueContainer = document.querySelector(`.${containerClass} .selected-value span`);
    const selectedService = selectedValueContainer ? selectedValueContainer.textContent.replace('.', '') : null;
    return selectedService;
}

function transferPlaylist(playlistName, fromContainerClass) {
    // slugged playlist name
    const playlistSlug = toSlug(playlistName);

    // determine the container classes for 'from' and 'to'
    const toContainerClass = fromContainerClass === 'from-container' ? 'to-container' : 'from-container';

    // get the playlist elements from both containers
    const fromPlaylistElement = document.querySelector(`.${fromContainerClass} #${playlistSlug}`);
    const toPlaylistElement = document.querySelector(`.${toContainerClass} #${playlistSlug}`);

    // move the playlist from 'from' to 'to' if it's not already there
    if (fromPlaylistElement && !toPlaylistElement) {
        const playlistElementToTransfer = fromPlaylistElement.cloneNode(true);
        playlistElementToTransfer.addEventListener('click', function() {
            transferPlaylist(playlistName, toContainerClass);
        });

        // remove the playlist from the 'from' container
        fromPlaylistElement.parentElement.removeChild(fromPlaylistElement);

        // add the playlist to the 'to' container
        const toPlaylistContainer = document.querySelector(`.${toContainerClass} #playlistContainer`);
        toPlaylistContainer.appendChild(playlistElementToTransfer);
    } else if (toPlaylistElement) {
        // yhe playlist is already in the 'to' container, so we need to move it back to 'from'
        const playlistElementToTransferBack = toPlaylistElement.cloneNode(true);
        playlistElementToTransferBack.addEventListener('click', function() {
            transferPlaylist(playlistName, fromContainerClass);
        });

        // remove the playlist from the 'to' container
        toPlaylistElement.parentElement.removeChild(toPlaylistElement);

        // add the playlist back to the 'from' container
        const fromPlaylistContainer = document.querySelector(`.${fromContainerClass} #playlistContainer`);
        fromPlaylistContainer.appendChild(playlistElementToTransferBack);
    }
}