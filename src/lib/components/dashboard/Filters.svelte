<script>
    export let data = [];
    export let selectedAreas = [];
    export let selectedAgeRanges = [];

    let uniqueAreas = [];
    let uniqueAgeRanges = [];

    $: {
        if(data.length > 0) {
            uniqueAreas = [...new Set(data.map(item => item.HealthArea))];
            uniqueAgeRanges = [...new Set(data.map(item => item.AgeRange))].sort();
        }
    }
</script>

<div>
    <h3 class="text-lg font-semibold mb-2">Health Area</h3>
    <div class="space-y-1">
        {#each uniqueAreas as area}
            <label class="flex items-center space-x-2 cursor-pointer">
                <input type="checkbox" bind:group={selectedAreas} value={area} />
                <span>{area}</span>
            </label>
        {/each}
    </div>
</div>

<div class="mt-4">
    <h3 class="text-lg font-semibold mb-2">Age Range</h3>
    <div class="space-y-1">
        {#each uniqueAgeRanges as range}
            <label class="flex items-center space-x-2 cursor-pointer">
                <input type="checkbox" bind:group={selectedAgeRanges} value={range} />
                <span>{range}</span>
            </label>
        {/each}
    </div>
</div>