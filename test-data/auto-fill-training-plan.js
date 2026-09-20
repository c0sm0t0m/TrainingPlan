/**
 * Development Helper: Auto-fill AI Training Plan Generator
 * 
 * This script can be run in the browser console when on the AI Training Plan Generator page
 * to automatically fill in test data.
 * 
 * Usage:
 * 1. Navigate to http://localhost:5173/ai-training-plan
 * 2. Open browser DevTools (F12)
 * 3. Copy this entire script into the console and press Enter
 * 4. The form will be automatically filled with test data
 */

(function() {
  console.log('🧪 Loading test data for AI Training Plan Generator...');
  
  // Calculate next Monday
  function getNextMonday() {
    const today = new Date();
    const day = today.getDay();
    const daysUntilMonday = day === 0 ? 1 : day === 1 ? 7 : 8 - day;
    const nextMonday = new Date(today);
    nextMonday.setDate(today.getDate() + daysUntilMonday);
    return nextMonday.toISOString().split('T')[0];
  }
  
  // Test configuration
  const testConfig = {
    eventName: "Berlin Marathon 2026",
    eventDate: "2026-09-27",
    eventDistance: "Marathon (42.195 km)",
    goalTime: "3:30:00",
    startDate: getNextMonday(),
    trainingDaysPerWeek: 5,
    preferredTrainingDays: ["monday", "tuesday", "thursday", "saturday", "sunday"],
    additionalNotes: "Tuesdays: Running track session at 6 pm always\nThursdays: 8pm swim technique session."
  };
  
  console.log('📋 Test Configuration:', testConfig);
  
  // Helper function to set input value and trigger React state update
  function setInputValue(selector, value) {
    const input = document.querySelector(selector);
    if (input) {
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype,
        'value'
      ).set;
      nativeInputValueSetter.call(input, value);
      
      const event = new Event('input', { bubbles: true });
      input.dispatchEvent(event);
      
      console.log(`✅ Set ${selector} = ${value}`);
      return true;
    } else {
      console.warn(`⚠️  Could not find ${selector}`);
      return false;
    }
  }
  
  // Helper function to click MUI Select and choose option
  function selectMuiOption(labelText, value) {
    const labels = Array.from(document.querySelectorAll('label'));
    const label = labels.find(l => l.textContent === labelText);
    
    if (!label) {
      console.warn(`⚠️  Could not find label: ${labelText}`);
      return false;
    }
    
    const selectId = label.getAttribute('for');
    const select = document.getElementById(selectId);
    
    if (!select) {
      console.warn(`⚠️  Could not find select for label: ${labelText}`);
      return false;
    }
    
    // Click to open dropdown
    select.click();
    
    // Wait for dropdown to open, then click option
    setTimeout(() => {
      const options = document.querySelectorAll('[role="option"]');
      const option = Array.from(options).find(opt => 
        opt.textContent.includes(value.toString())
      );
      
      if (option) {
        option.click();
        console.log(`✅ Selected ${labelText} = ${value}`);
      } else {
        console.warn(`⚠️  Could not find option: ${value}`);
      }
    }, 100);
    
    return true;
  }
  
  // Helper function to toggle day chips
  function toggleDayChips(days) {
    const allDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
    
    allDays.forEach(day => {
      const chip = Array.from(document.querySelectorAll('[role="button"]')).find(el => 
        el.textContent.toLowerCase().includes(day)
      );
      
      if (chip) {
        const shouldBeSelected = days.includes(day);
        const isSelected = chip.classList.contains('MuiChip-filled') || 
                          chip.getAttribute('aria-pressed') === 'true';
        
        if (shouldBeSelected !== isSelected) {
          chip.click();
          console.log(`✅ Toggled ${day}`);
        }
      }
    });
  }
  
  console.log('\n🚀 Filling form fields...\n');
  
  // Step 1: Fill event details (if on step 0)
  setTimeout(() => {
    setInputValue('input[label="Event Name"]', testConfig.eventName);
    setInputValue('input[type="date"][label="Event Date"]', testConfig.eventDate);
    setInputValue('input[label="Target Distance"]', testConfig.eventDistance);
    setInputValue('input[label="Goal Time"]', testConfig.goalTime);
    
    // Alternative selectors for Material-UI inputs
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
      const id = input.id || '';
      const name = input.name || '';
      const label = input.getAttribute('aria-label') || '';
      
      if (id.includes('event') || label.includes('Event Name') || 
          input.previousElementSibling?.textContent?.includes('Event Name')) {
        setInputValue(`#${id}`, testConfig.eventName);
      }
      
      if (input.type === 'date' && (label.includes('Event Date') || 
          input.previousElementSibling?.textContent?.includes('Event Date'))) {
        setInputValue(`#${id}`, testConfig.eventDate);
      }
      
      if (id.includes('distance') || label.includes('Distance')) {
        setInputValue(`#${id}`, testConfig.eventDistance);
      }
      
      if (id.includes('goal') || label.includes('Goal Time')) {
        setInputValue(`#${id}`, testConfig.goalTime);
      }
    });
  }, 500);
  
  // Step 2: Fill plan configuration (if on step 1)
  setTimeout(() => {
    setInputValue('input[type="date"][label="Plan Start Date"]', testConfig.startDate);
    
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
      const label = input.previousElementSibling?.textContent || '';
      if (label.includes('Plan Start') || label.includes('Start Date')) {
        setInputValue(`#${input.id}`, testConfig.startDate);
      }
    });
    
    // Select training days per week
    selectMuiOption('Training Days Per Week', testConfig.trainingDaysPerWeek);
    
    // Toggle day chips
    setTimeout(() => {
      toggleDayChips(testConfig.preferredTrainingDays);
    }, 500);
  }, 1000);
  
  // Step 2: Fill additional notes
  setTimeout(() => {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
      const label = textarea.previousElementSibling?.textContent || '';
      if (label.includes('Additional') || label.includes('Notes') || label.includes('Constraints')) {
        const nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(
          window.HTMLTextAreaElement.prototype,
          'value'
        ).set;
        nativeTextAreaValueSetter.call(textarea, testConfig.additionalNotes);
        
        const event = new Event('input', { bubbles: true });
        textarea.dispatchEvent(event);
        
        console.log(`✅ Set additional notes`);
      }
    });
  }, 1500);
  
  console.log('\n✨ Test data loading complete!');
  console.log('📝 Note: You may need to manually verify some fields depending on the current step.');
  console.log('🔄 If fields are not filled, try advancing to the next step and running this script again.');
})();
