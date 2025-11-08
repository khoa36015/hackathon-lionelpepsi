<script>
	import '../app.css';
	import OptionToggle from '$lib/components/OptionToggle.svelte';
	import { chosenOption, ensureData } from '$lib/stores/ChosenOption.js';
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import favicon from '$lib/assets/favicon.svg';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';

	let showOptionModal = false;

	onMount(async () => {
		if (!get(chosenOption)) {
		showOptionModal = true;
		} else {
		await ensureData(get(chosenOption));
		}
	});

</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<OptionToggle />

<Header />
<slot />
<Footer />
