<script>
	import "@evidence-dev/tailwind/fonts.css";
	import "../app.css";
	import { EvidenceDefaultLayout } from "@evidence-dev/core-components";
	export let data;
</script>

<EvidenceDefaultLayout
	{data}
	title="Edwin's Analytics"
	neverShowQueries="True"
	hideSidebar="True"
	githubRepo="https://github.com/notedwin"
>
	<slot slot="content" />
</EvidenceDefaultLayout>
