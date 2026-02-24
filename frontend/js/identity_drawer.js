async function loadIdentity(identity) {

    const response = await fetch(`/intel/identity/${identity}`);
    const profile = await response.json();

    document.getElementById("identityDrawer").innerText =
        JSON.stringify(profile, null, 2);
}
